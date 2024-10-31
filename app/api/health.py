import logging
import logging.config

from fastapi import APIRouter
from pydantic import (
    AliasGenerator,
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic.alias_generators import to_camel

logger = logging.getLogger(__name__)


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        str_max_length=500000,
    )


class HealthModel(BaseSchema):
    status: str = Field(description="API Health status")


health_router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@health_router.get(
    "/",
    summary="Get API ASGI app health endpoint",
)
async def get_health() -> HealthModel:
    logger.info("Health endpoint pinged")
    return HealthModel(status="OK")
