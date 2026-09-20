import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedBase


class StudentProfile(Base, TimestampedBase):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # institution_id is what Flow C (academician skill-gap report) aggregates against.
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    enrollment_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(150), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(150), nullable=True)
    semester: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    career_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_interests: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    preferred_locations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    open_to_remote: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    profile_completion_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship()
    institution: Mapped["Organization | None"] = relationship()


class AcademicianProfile(Base, TimestampedBase):
    __tablename__ = "academician_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # institution_id drives which institution's skill-gap report this academician sees.
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    employee_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(150), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    research_interests: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_completion_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship()
    institution: Mapped["Organization | None"] = relationship()


class IndustryProfile(Base, TimestampedBase):
    __tablename__ = "industry_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True
    )
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(150), nullable=True)
    expertise: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship()
    organization: Mapped["Organization | None"] = relationship()
