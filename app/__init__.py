import logging
import os

from app.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
logger.info(f'LOG_LEVEL: {os.environ.get("LOG_LEVEL")}')

config = Config()


def initialize_psql_session() -> Session:
    logger.info("Initializing PSQL Connection")
    engine = create_engine(config.postgres_conn_url, echo=True)

    logger.info("Initializing PSQL Session")
    base = declarative_base()
    session = Session(bind=engine)
    logger.info("Initialized PSQL Session")

    create_schema_and_tables(engine=engine, session=session, base=base)

    return session


def create_schema_and_tables(engine, session, base):
    inspector = inspect(engine)

    # Check if schema "test_app" exists
    schema_name = "test_app"
    if schema_name not in inspector.get_schema_names():
        try:
            with engine.begin() as connection:
                connection.execute(CreateSchema(schema_name))
            logger.info(f"Schema '{schema_name}' created successfully.")
        except Exception as e:
            logger.warning(
                f"Schema '{schema_name}' already exists or an error occurred: {e}"
            )
    else:
        logger.info(f"Schema '{schema_name}' already exists.")

    # Import ORM models and define tables
    from app.model.psql.orm import ClaimModel, ClaimDetailModel, PatientModel, ProviderModel

    # Define table list and check each table’s existence
    tables = [
        PatientModel.__table__,
        ProviderModel.__table__,
        ClaimDetailModel.__table__,
        ClaimModel.__table__,
    ]

    # base.metadata.drop_all(engine, tables=tables)

    # Only create tables that don’t exist
    try:
        base.metadata.create_all(
            engine,
            tables=[
                table
                for table in tables
                if not inspector.has_table(table.name, schema=schema_name)
            ],
        )
        session.commit()
        logger.info("Tables initialized successfully!")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"An error occurred: {str(e)}")


postgres_conn = initialize_psql_session()
