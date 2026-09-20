"""
Import every model module here so:
1. Alembic's autogenerate can see all tables via Base.metadata.
2. String-based relationship() references (e.g. "UserRole") resolve correctly,
   since SQLAlchemy needs all classes registered before mappers configure.

Order doesn't matter for imports (SQLAlchemy resolves relationships lazily by
class name), but every model module must be listed here.
"""

from app.models.role import Role  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
from app.models.organization import Organization, OrganizationMember  # noqa: F401
from app.models.profile import AcademicianProfile, IndustryProfile, StudentProfile  # noqa: F401
from app.models.skill import Skill, SkillCategory, UserSkill  # noqa: F401
from app.models.opportunity import Opportunity, OpportunitySkill  # noqa: F401
from app.models.application import Application  # noqa: F401
