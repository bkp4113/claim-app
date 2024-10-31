import logging
import logging.config
import traceback
from datetime import UTC, datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.param_functions import Header, Path, Query
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError

from app import postgres_conn
from app.authorizer.authorizer import authenticate_user
from app.model.api.claims import (
    Claim,
    ClaimResponseModel,
    ClaimsResponseModel,
    TooMayRequests,
    TopProviderFees,
    ClaimResourceResponseModel,
    standard_responses,
)
from app.model.psql.orm import ClaimDetailModel, ClaimModel, PatientModel, ProviderModel

logger = logging.getLogger(__name__)


int_path_identifier = Annotated[
    int,
    Path(
        title="Claim identifier",
        description="Claim identifier",
        lt=10000,
    ),
]


claims_router = APIRouter(
    prefix="/claims",
    tags=["claims"],
    dependencies=[Depends(authenticate_user, use_cache=True)],
)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


async def _calculate_net_fee(claim: Claim):
    # net fee formula
    # *“net fee” = “provider fees” + “member coinsurance” + “member copay” - “Allowed fees”* (note again that the names are not consistent in capitalization).
    net_fees = (
        claim.provider_fees + claim.member_co_insurance + claim.member_co_pay
    ) - claim.allowed_fees

    logger.info(f"Claim:{claim.submitted_procedure} net_fees:{net_fees}")

    return net_fees


# NOTE:
# The static route must remain at top to avoid conflict with dynamic route ex. /claims must be defined before GET /{claimId}
# The authenticate_user and dependency is for illustration purpose only, the actual implementation would does below.
#  - Authenticate user with JWT
#  - Validate Roles/Scope
#  - Validate tenancy if multi tenant arch.


# TODO: Implement the get_claims
@claims_router.get(
    "/",
    responses={**standard_responses},
    summary="List all claims paginated (Sorted by desc created time)",
)
async def get_claims(
    limit: Annotated[
        int,
        Query(
            title="Limit of claims to get", description="Limit of claims to get", le=100
        ),
    ] = 100,
    auth: dict = Depends(authenticate_user, use_cache=True),
) -> ClaimsResponseModel:  # ClaimsResponseModel:
    logger.info(f"Getting list of claims for limit: {limit} userId:{auth['sub']}")

    # TODO: Run query on Claims ORM and return list of claims within pagination limit

    logger.info(f"Returning list of claims for userId:{auth['sub']}")
    claims = [
        ClaimResponseModel(
            claimId=i,
            createdAt=datetime.now(UTC).isoformat(),
            updatedAt=datetime.now(UTC).isoformat(),
        )
        for i in range(0, 10)
    ]
    return ClaimsResponseModel(claims=claims[0:limit], totalCount=len(claims))


@claims_router.post(
    "/",
    responses={
        **standard_responses,
    },
    summary="Process new claim",
)
async def process_claim(
    claims: List[Claim],
    x_test: str = Header(None, description="Custom x headers for demo"),
    auth: dict = Depends(authenticate_user, use_cache=True),
) -> ClaimResponseModel:
    # NOTE: Assuming claims received as a batch, Processing as a batch and allow
    # creation of subscriber and provider during processing batch. In actual impl.
    # this would have been solved by either creating the subscriber or provider before ingesting
    # this event for processing or via another ms
    logger.info(f"Processing claim for user: {auth['sub']}")

    try:
        # Create placeholder claim
        with postgres_conn as db_session:
            claim_model = ClaimModel()
            db_session.add(claim_model)
            # Commit to generate claim_id for claim_model
            db_session.commit()
            db_session.flush()

            # Capture claim_id and timestamps immediately after flush
            claim_id = claim_model.claim_id
            created_at = claim_model.created
            updated_at = claim_model.updated

            # Create ClaimDetailModel instances with valid claim_id
            providers_npi = []
            subscribers_id = []
            claims_details = []

            for claim in claims:
                net_fees = await _calculate_net_fee(claim=claim)

                providers_npi.append(claim.npi)
                subscribers_id.append(claim.subscriber)

                # Populate each claim_detail with the correct claim_id
                claims_details.append(
                    ClaimDetailModel(
                        claim_id=claim_id,
                        service_date=claim.service_date,
                        submitted_procedure=claim.submitted_procedure,
                        quadrant=claim.quadrant,
                        group=claim.group,
                        allowed_fees=claim.allowed_fees,
                        provider_fees=claim.provider_fees,
                        member_co_insurance=claim.member_co_insurance,
                        member_co_pay=claim.member_co_pay,
                        net_fees=net_fees,
                    )
                )

            # Batch query existing providers and subscribers
            existing_providers = (
                db_session.query(ProviderModel)
                .filter(ProviderModel.npi.in_(providers_npi))
                .all()
            )
            existing_subscribers = (
                db_session.query(PatientModel)
                .filter(PatientModel.subscriber_id.in_(subscribers_id))
                .all()
            )

            existing_provider_npis = {
                provider.npi: provider.provider_id for provider in existing_providers
            }
            existing_subscriber_ids = {
                subscriber.subscriber_id: subscriber.patient_id
                for subscriber in existing_subscribers
            }

            # Create new providers
            new_providers = []
            for npi in set(providers_npi) - set(existing_provider_npis.keys()):
                provider = ProviderModel(npi=npi)
                new_providers.append(provider)

            # Create new subscribers
            new_subscribers = []
            for subscriber_id in set(subscribers_id) - set(
                existing_subscriber_ids.keys()
            ):
                subscriber = PatientModel(subscriber_id=subscriber_id)
                new_subscribers.append(subscriber)

            # Add new providers and subscribers in bulk
            if new_providers or new_subscribers:
                db_session.add_all(new_providers + new_subscribers)
                db_session.commit()

                # Update provider and subscriber IDs for the newly created entries
                for provider in new_providers:
                    existing_provider_npis[provider.npi] = provider.provider_id
                for subscriber in new_subscribers:
                    existing_subscriber_ids[subscriber.subscriber_id] = (
                        subscriber.patient_id
                    )

            # Update claim details with correct provider and subscriber IDs
            for i, detail in enumerate(claims_details):
                if claims[i].npi in existing_provider_npis:
                    detail.provider_id = existing_provider_npis[claims[i].npi]
                if claims[i].subscriber in existing_subscriber_ids:
                    detail.subscriber_id = existing_subscriber_ids[claims[i].subscriber]

            # Step 8: Add claim details in bulk
            db_session.add_all(claims_details)
            db_session.commit()

        # Assumption on payment processing
        # - Payment processing shall be handled asynchronously via Queue or Stream and claim detail shall be dumped which is inclusive of net_fees
        # - Error Handling: If in the event of queue or stream is down, the API need to rollback psql commit
        # - If queue is opted, then DLQ shall be setup to redrive the dead messages
        # - If stream is opted, then stream event handler shall resume from where left of

        # Return response
        return ClaimResponseModel(
            claimId=claim_id,
            createdAt=created_at.isoformat(),
            updatedAt=updated_at.isoformat(),
        )
    except SQLAlchemyError as s:
        logger.error(f"SQLAlchemyError: {s}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db_session.rollback()
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


# TODO: Implement the get_claims_by_id for now it's placeholder
@claims_router.get(
    "/{claimId}",
    responses={**standard_responses},
    summary="Get a given claims by ID",
)
async def get_claims_by_id(
    claimId: int_path_identifier,
    auth: dict = Depends(authenticate_user, use_cache=True),
) -> List[ClaimResourceResponseModel]:
    logger.info(f"Getting claimId:{claimId} userId:{auth['sub']}")

    try:
        with postgres_conn as db_session:

            claim = (
                db_session.query(ClaimModel)
                .filter_by(claim_id=claimId)
                .first()
            )

            if not claim:
                raise HTTPException(
                    detail=f"Given claimId:{claimId} not found.",
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                )
            # Query to aggregate net fees by provider_npi
            claim_query = db_session.query(ClaimDetailModel).filter_by(claim_id=claimId)

            claims = db_session.execute(claim_query).scalars().fetchall()

            logger.info(f"Returning claim:{claimId} for userId:{auth['sub']}")
            # Return the result
            return [
                ClaimResourceResponseModel(
                    claimId=row.claim_id,
                    service_date=row.service_date.isoformat(),
                    group=row.group,
                    subscriber=row.patient.subscriber_id,
                    npi=row.provider.npi,
                    quadrant=row.quadrant,
                    submitted_procedure=row.submitted_procedure,
                    provider_fees=row.provider_fees,
                    allowed_fees=row.allowed_fees,
                    member_co_insurance=row.member_co_insurance,
                    member_co_pay=row.member_co_pay,
                    net_fees=row.net_fees,
                    createdAt=row.created.isoformat(),
                    updatedAt=row.updated.isoformat(),
                )
                for row in claims
            ]

    except SQLAlchemyError as s:
        logger.error(f"SQLAlchemyError: {s}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db_session.rollback()
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )


@claims_router.get(
    "/top-providers/",
    responses={
        **standard_responses,
        **{
            429: {"model": TooMayRequests},
        },
    },
)
# Using the slow API module to achieve the rate limiting based on client ip
# In actual implementation, I would have used WAF, API or Lambda Level throttling
# The alternative could have been building custom i/o based solution which works as
# pre flight to track the request and
@limiter.limit("10/minute")
async def get_top_providers(
    request: Request, auth: dict = Depends(authenticate_user, use_cache=True)
) -> List[TopProviderFees]:
    logger.info(f"Getting top providers by net fees for userId:{auth['sub']}")
    try:
        with postgres_conn as db_session:
            # Query to aggregate net fees by provider_npi
            result = (
                db_session.query(
                    ProviderModel.npi.label("provider_npi"),  # Select NPI directly
                    func.sum(ClaimDetailModel.net_fees).label("total_net_fees"),
                )
                .join(
                    ClaimDetailModel,
                    ClaimDetailModel.provider_id == ProviderModel.provider_id,
                )  # Join on provider_id
                .group_by(ProviderModel.npi)  # Group by provider_npi
                .order_by(
                    desc("total_net_fees")
                )  # Order by total_net_fees in descending order
                .limit(10)  # Limit to top 10 results
                .all()
            )

        logger.info(f"Returning top providers by net fees for userId:{auth['sub']}")
        # Return the result
        return [
            TopProviderFees(
                provider_npi=row.provider_npi, total_net_fees=row.total_net_fees
            )
            for row in result
        ]

    except SQLAlchemyError as s:
        logger.error(f"SQLAlchemyError: {s}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        db_session.rollback()
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            detail="Internal Server Error",
            status_code=500,
            headers={"Content-Type": "application/json"},
        )
