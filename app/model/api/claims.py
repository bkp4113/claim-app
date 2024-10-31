from typing import List, Optional

from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        str_max_length=500000,
    )


# class Base(DeclarativeBase):
#     pass

# service date,"submitted procedure",quadrant,"Plan/Group #",Subscriber#,"Provider NPI","provider fees","Allowed fees","member coinsurance","member copay"
# 3/28/18 0:00,D0180,,GRP-1000,3730189502,1497775530,$100.00 ,$100.00 ,$0.00 ,$0.00
# 3/28/18 0:00,D0210,,GRP-1000,3730189502,1497775530,$108.00 ,$108.00 ,$0.00 ,$0.00
# 3/28/18 0:00,D4346,,GRP-1000,3730189502,1497775530,$130.00 ,$65.00 ,$16.25 ,$0.00
# 3/28/18 0:00,D4211,UR,GRP-1000,3730189502,1497775530,$178.00 ,$178.00 ,$35.60 ,$0.00


class Claim(BaseSchema):
    service_date: str = Field(
        description="Claim service data",
        alias="service date",
    )
    submitted_procedure: str = Field(
        description="Claim submitted procedure",
        alias="submitted procedure",
    )
    quadrant: Optional[str] = Field(description="Claim quadrant", alias="quadrant")
    group: str = Field(
        description="Claim group", alias="Plan/Group #"
    )
    subscriber: str = Field(
        description="Claim subscriber",
        alias="Subscriber#",
        coerce_numbers_to_str=True,
    )
    npi: str = Field(
        description="Claim provider",
        alias="Provider NPI",
        coerce_numbers_to_str=True,
    )
    provider_fees: str = Field(
        description="Claim provider fees",
        alias="provider fees",
    )
    allowed_fees: str = Field(
        description="Claim allowed fees",
        alias="Allowed fees",
    )
    member_co_insurance: str = Field(
        description="Claim member co-insurance",
        alias="member coinsurance",
    )
    member_co_pay: str = Field(
        description="Claim member co-pay",
        alias="member copay",
    )

    @field_validator("submitted_procedure")
    def default_submitted_procedure(cls, v):
        """
        Custom validator for submitted_procedure
        """

        if v[0] != "D":
            raise ValueError("submitted procedure must start with D always")

        return v

    @field_validator("npi")
    def default_npi(cls, v):
        """
        Custom validator for npi
        """

        if not v.isdigit() or len(v) != 10:
            raise ValueError("Provider NPI must be always 10 digit integer value")

        return v

    # @model_validator(mode="before")
    # def validate_payment_fields(cls, values):
    #     for field_name in [
    #         "provider fees",
    #         "Allowed fees",
    #         "member coinsurance",
    #         "member copay",
    #     ]:
    #         values[field_name] = cls._strip_dollar_sign_and_convert(
    #             field_name,
    #             values[field_name]
    #         )
    #     return values

    @model_validator(mode="after")
    def transform_payment_fields(cls, values):
        for field_name in [
            "provider_fees",
            "allowed_fees",
            "member_co_insurance",
            "member_co_pay",
        ]:
            setattr(
                values,
                field_name,
                cls._strip_dollar_sign_and_convert(field_name, getattr(values, field_name)),
            )
        return values

    @classmethod
    def _strip_dollar_sign_and_convert(cls, field_name, v):
        if isinstance(v, str):
            v = v.replace("$", "").strip()
        else:
            raise ValueError(f"{field_name} must be always start with $")

        try:
            value = float(v)
        except ValueError:
            raise ValueError(f"{field_name} must be always e.g., '$10.00'")

        return value


# class ProviderOrm(Base):
#     __tablename__ = "provider"

#     id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
#     npi: Mapped[str] = mapped_column(nullable=False)
#     createdAt: str = Field(
#         description="Claim created at as UTC ISO timestamp.",
#         validation_alias="created_at",
#     )
#     updatedAt: str | None = Field(
#         description="Claim updated at as UTC ISO timestamp.",
#         validation_alias="updated_at",
#         default=None,
#     )


# class ProviderModel(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     id: int
#     npi: Annotated[str, StringConstraints(max_length=20)]
#     domains: List[Annotated[str, StringConstraints(max_length=255)]]


class ClaimResponseModel(BaseModel):
    claimId: int = Field(description="Claim identifier")
    createdAt: str = Field(
        description="Claim created at as UTC ISO timestamp.",
    )
    updatedAt: str | None = Field(
        description="Claim updated at as UTC ISO timestamp.",
        default=None,
    )


class ClaimsResponseModel(BaseModel):
    claims: List[ClaimResponseModel] = Field(description="Claims")
    totalCount: int = Field(description="Total processed claims")


class ClaimResourceResponseModel(BaseModel):
    claimId: int = Field(description="Claim identifier")
    service_date: str = Field(
        description="Claim service data",
    )
    submitted_procedure: str = Field(
        description="Claim submitted procedure",
    )
    quadrant: Optional[str] = Field(description="Claim quadrant")
    group: str = Field(description="Claim group")
    subscriber: str = Field(
        description="Claim subscriber",
    )
    npi: str = Field(
        description="Claim provider",
    )
    provider_fees: float = Field(
        description="Claim provider fees",
    )
    allowed_fees: float = Field(
        description="Claim allowed fees",
    )
    member_co_insurance: float = Field(
        description="Claim member co-insurance",
    )
    member_co_pay: float = Field(
        description="Claim member co-pay",
    )
    net_fees: float = Field(
        description="Claim net fees",
    )
    createdAt: str = Field(
        description="Claim created at as UTC ISO timestamp.",
    )
    updatedAt: str | None = Field(
        description="Claim updated at as UTC ISO timestamp.",
        default=None,
    )



class TopProviderFees(BaseModel):
    provider_npi: str
    total_net_fees: float


class AuthenticationResponseMessage(BaseModel):
    detail: str = Field(default="Authentication Required.")


class TooMayRequests(BaseModel):
    detail: str = Field(default="Too Many Requests.")


class NotFoundResponseMessage(BaseModel):
    detail: str = Field(default="Given identifier resource not found.")


class InternalServerErrorMessage(BaseModel):
    detail: str = Field(default="Internal Server Error.")


standard_responses = {
    401: {"model": AuthenticationResponseMessage},
    404: {"model": NotFoundResponseMessage},
    500: {"model": InternalServerErrorMessage},
}
