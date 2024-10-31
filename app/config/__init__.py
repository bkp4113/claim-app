import json
from os import environ


# Initialize app configuration
class Config(object):
    # Alternatively the config can be initialized from encrypted env file living in same dir
    def __init__(self) -> None:
        try:
            self.environment = environ["ENVIRONMENT"]
            self.app_log_level = environ.get("APP_LOG_LEVEL", "INFO")
            self.api_log_level = environ.get("API_LOG_LEVEL", "INFO")
            self.disable_existing_logger = json.loads(
                environ.get("DISABLE_EXISTING_LOGGER", "false")
            )
            self.cors_allowed_origin = environ.get("CORS_ALLOWED_ORIGIN", "*")
            self.cors_allowed_headers = environ.get("CORS_ALLOWED_HEADERS", "*")
            self.cors_allowed_methods = environ.get("CORS_ALLOWED_METHODS", "*")

            self.postgres_conn_url = environ["DATABASE_URL"]
        except KeyError as e:
            raise RuntimeError(f"Environment variable {e} is missing")