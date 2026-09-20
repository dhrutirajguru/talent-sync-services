import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedBase


class SkillCategory(Base, TimestampedBase):
    __tablename__ = "skill_categories"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")

    skills: Mapped[list["Skill"]] = relationship(back_populates="category")


class Skill(Base, TimestampedBase):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("category_id", "name", name="uq_skills_category_name"),)

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_categories.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skill_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")

    category: Mapped["SkillCategory | None"] = relationship(back_populates="skills")


class UserSkill(Base, TimestampedBase):
    """
    A user's declared/assessed proficiency in a skill.

    Demo scope note (Section 6.1): the assessment quiz itself isn't built —
    rows here are pre-seeded directly (source='SELF_DECLARED') so the
    dashboard and matching engine work against real data from day one.
    """
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skills_user_skill"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False
    )
    proficiency_level: Mapped[str] = mapped_column(String(30), nullable=False)
    proficiency_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    years_experience: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="SELF_DECLARED")
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship()
    skill: Mapped["Skill"] = relationship()
