import os
import json
import contextvars
from app.api import health, claims
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app import config

from starlette.middleware.base import BaseHTTPMiddleware


import logging
import logging.config


request_id_context = contextvars.ContextVar("request_id", default="N/A")


class ContextAwareFormatter(logging.Formatter):
    def format(self, record):
        record.trace_id = request_id_context.get("N/A")
        return super().format(record)


# Define the logging middleware for cloud deployment
async def log_trace_id(request: Request, call_next):
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request client: {request.client}")
    # In actual application this could have been "x-forwarded-for"
    trace_id = f"{request.headers.get('host', 'N/A')}"

    # Log or set the trace ID in context for further processing/logging
    request_id_context.set(trace_id)

    response = await call_next(request)
    return response


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": ContextAwareFormatter,
            "fmt": "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s [Trace ID: %(trace_id)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": ContextAwareFormatter,
            "fmt": "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s [Trace ID: %(trace_id)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": config.app_log_level,
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": config.api_log_level,
            "propagate": False,
        },
    },
}


logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


production_url = "https://somedomain.com"
dev_url = "https://dev.somedomain.com"
local_url = "http://localhost:8080"

DISABLE_SWAGGER = json.loads(os.environ.get("DISABLE_SWAGGER", "true").lower())

doc_config = {"redoc_url": None}

if DISABLE_SWAGGER:
    doc_config["docs_url"] = None


def custom_openapi():
    if app.openapi_schema:
        app.openapi_version = "3.0.0"
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Claim Processor REST APIs",
        version="1.0.0",
        summary="Claim Processor REST APIs.",
        description="Claim Processor REST endpoints",
        routes=app.routes,
        servers=[
            {"url": production_url, "description": "Production server"},
            {"url": dev_url, "description": "Dev server"},
            {"url": local_url, "description": "Local development server"},
        ],
        openapi_version="3.0.0",
    )
    openapi_schema["components"] = {
        **openapi_schema["components"],
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
    }
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app():
    logger.info("Creating Claim Processor Application")
    app = FastAPI(
        **doc_config,
    )

    logger.info("Configuring Claim Processor App OpenAPI Specs")
    app.openapi = custom_openapi

    app.contact = {"Maintainer/Author": "bhaumik.p.0110@gmail.com"}

    logger.info("Configuring Claim Processor App CORS")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_allowed_origin.split(","),
        allow_credentials=True,
        allow_methods=config.cors_allowed_methods.split(","),
        allow_headers=config.cors_allowed_headers.split(","),
    )

    app.include_router(claims.claims_router, prefix="/v1")
    app.include_router(health.health_router, include_in_schema=False)

    logger.info("Created Claim Processor Application")

    return app


logger.info("Starting Claim Processor Application")
app = create_app()
logger.info("Started Claim Processor Application")

# Add the logging middleware using BaseHTTPMiddleware
app.add_middleware(BaseHTTPMiddleware, dispatch=log_trace_id)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app)
