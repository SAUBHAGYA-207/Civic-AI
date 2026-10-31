import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import (
    String, Text, Float, Integer, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    complaint_text: Mapped[str] = mapped_column(Text, nullable=False)
    issue_category: Mapped[str] = mapped_column(String(50), default="unknown", index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    address_or_landmark: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    workflow_status: Mapped[str] = mapped_column(String(50), default="submitted", index=True)
    review_pathway: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    department_recommendation: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)

    # Relationships
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="report", cascade="all, delete-orphan")
    evidence_records: Mapped[list["EvidenceRecord"]] = relationship("EvidenceRecord", back_populates="report", cascade="all, delete-orphan")
    triage_decisions: Mapped[list["TriageDecision"]] = relationship("TriageDecision", back_populates="report", cascade="all, delete-orphan")
    status_history: Mapped[list["StatusHistory"]] = relationship("StatusHistory", back_populates="report", cascade="all, delete-orphan", order_by="StatusHistory.created_at")

class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    report: Mapped["Report"] = relationship("Report", back_populates="attachments")

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    image_evidence_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    text_evidence_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    fused_evidence_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    model_identifiers: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    report: Mapped["Report"] = relationship("Report", back_populates="evidence_records")

class TriageDecision(Base):
    __tablename__ = "triage_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    rule_version: Mapped[str] = mapped_column(String(20), default="v1.0.0")
    recommended_pathway: Mapped[str] = mapped_column(String(50), nullable=False)
    reason_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    decision_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    report: Mapped["Report"] = relationship("Report", back_populates="triage_decisions")

class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id: Mapped[str] = mapped_column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(50), default="reviewer")
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    report: Mapped["Report"] = relationship("Report", back_populates="status_history")
