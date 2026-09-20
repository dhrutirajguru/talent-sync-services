from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampedBase


class Role(Base, TimestampedBase):
    """
    Reference table: STUDENT, ACADEMICIAN, INDUSTRY, INSTITUTION_ADMIN, PLATFORM_ADMIN.
    Seeded once at startup — see app/seed.py.
    """
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role")
