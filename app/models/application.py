import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedBase


class Application(Base, TimestampedBase):
    """
    Demo scope note (Section 6.1): resume_document_id from the full design
    doc schema is intentionally omitted — the documents/S3 upload flow is
    deferred, and applications don't need an attached resume to demonstrate
    the Student → apply → Industry sees applicant loop.
    """
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "applicant_user_id", name="uq_applications_opp_applicant"),
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id"), nullable=False
    )
    applicant_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SUBMITTED")
    status_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    opportunity: Mapped["Opportunity"] = relationship()
    applicant: Mapped["User"] = relationship()
