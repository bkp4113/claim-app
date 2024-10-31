import logging
import os

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Float,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(os.environ.get("LOG_LEVEL", "INFO"))

Base = declarative_base()


class ProviderModel(Base):
    __tablename__ = "provider"
    __table_args__ = (
        Index("provider_id_key", "provider_id", unique=True),
        {"schema": "test_app"},
    )

    provider_id = Column(
        Integer(), primary_key=True, nullable=False, autoincrement=True
    )
    npi = Column(Text(), nullable=False)
    created = Column(TIMESTAMP, server_default=text("now()"))
    updated = Column(TIMESTAMP, server_default=text("now()"))

    # Relationship to ClaimDetailModel
    claim_details = relationship("ClaimDetailModel", back_populates="provider")


class PatientModel(Base):
    __tablename__ = "patient"
    __table_args__ = (
        Index("patient_id_key", "patient_id", unique=True),
        {"schema": "test_app"},
    )

    patient_id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    subscriber_id = Column(Text(), nullable=False)
    created = Column(TIMESTAMP, server_default=text("now()"))
    updated = Column(TIMESTAMP, server_default=text("now()"))

    # Relationship to ClaimDetailModel
    claim_details = relationship("ClaimDetailModel", back_populates="patient")


class ClaimDetailModel(Base):
    __tablename__ = "claim_detail"
    __table_args__ = (
        Index("claim_detail_claim_id_key", "claim_id", unique=False),
        {"schema": "test_app"},
    )

    id = Column(Integer(), primary_key=True, autoincrement=True)
    claim_id = Column(
        Integer(),
        ForeignKey("test_app.claim.claim_id"),
        nullable=False,
    )
    subscriber_id = Column(
        Integer(), ForeignKey("test_app.patient.patient_id"), nullable=False
    )
    provider_id = Column(
        Integer(), ForeignKey("test_app.provider.provider_id"), nullable=False
    )
    service_date = Column(TIMESTAMP, nullable=False)
    submitted_procedure = Column(Text(), nullable=False)
    quadrant = Column(Text(), nullable=True)
    group = Column(Text(), nullable=False)
    provider_fees = Column(Float(), nullable=False)
    allowed_fees = Column(Float(), nullable=False)
    member_co_insurance = Column(Float(), nullable=False)
    member_co_pay = Column(Text(), nullable=False)
    net_fees = Column(Float(), nullable=False)
    created = Column(TIMESTAMP, server_default=text("now()"))
    updated = Column(TIMESTAMP, server_default=text("now()"))

    # Relationships
    provider = relationship("ProviderModel", back_populates="claim_details")
    patient = relationship("PatientModel", back_populates="claim_details")
    claim = relationship("ClaimModel", back_populates="claim_details")


class ClaimModel(Base):
    __tablename__ = "claim"
    __table_args__ = (
        Index("claim_id_key", "claim_id", unique=True),
        {"schema": "test_app"},
    )

    claim_id = Column(Integer(), primary_key=True, nullable=False, autoincrement=True)
    created = Column(TIMESTAMP, server_default=text("now()"))
    updated = Column(TIMESTAMP, server_default=text("now()"))

    # Relationship to ClaimDetailModel
    claim_details = relationship("ClaimDetailModel", back_populates="claim")
