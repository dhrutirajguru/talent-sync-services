import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedBase


class Opportunity(Base, TimestampedBase):
    """
    Demo scope note: the search_vector generated column from the design doc's
    full DDL (Section 5.7) is intentionally omitted here — full-text search is
    deferred (Section 6.1). Plain filtering is enough for the demo's seeded
    handful of postings; add the column via an Alembic migration when search
    is turned on, without changing this model's other fields.
    """
    __tablename__ = "opportunities"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String(30), nullable=True)
    duration_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    stipend_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), default="INR", nullable=True)
    application_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    eligibility_criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_cgpa: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    openings_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship()
    creator: Mapped["User"] = relationship()
    required_skills: Mapped[list["OpportunitySkill"]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )


class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "skill_id", name="uq_opportunity_skills_opp_skill"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False
    )
    required_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    importance: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM")
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    opportunity: Mapped["Opportunity"] = relationship(back_populates="required_skills")
    skill: Mapped["Skill"] = relationship()
