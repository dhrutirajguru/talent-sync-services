import uuid

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, OpportunitySkill
from app.models.profile import StudentProfile
from app.models.skill import Skill, UserSkill


class InstitutionRepository:
    """
    Backs Flow C (Academician skill-gap report). Deliberately reuses the
    existing skills/opportunities/student_profiles tables — no curriculum
    entity, per the design doc's Section 6.1 scoping.
    """

    def __init__(self, db: Session):
        self.db = db

    def count_students(self, institution_id: uuid.UUID) -> int:
        stmt = select(func.count(StudentProfile.id)).where(StudentProfile.institution_id == institution_id)
        return self.db.execute(stmt).scalar_one()

    def demand_by_skill(self) -> dict[uuid.UUID, int]:
        """How many live (PUBLISHED) opportunities, across every organization,
        require each skill."""
        stmt = (
            select(OpportunitySkill.skill_id, func.count(distinct(OpportunitySkill.opportunity_id)))
            .join(Opportunity, Opportunity.id == OpportunitySkill.opportunity_id)
            .where(Opportunity.status == "PUBLISHED")
            .group_by(OpportunitySkill.skill_id)
        )
        return {row[0]: row[1] for row in self.db.execute(stmt).all()}

    def supply_by_skill(self, institution_id: uuid.UUID) -> dict[uuid.UUID, int]:
        """How many of this institution's students already have each skill."""
        stmt = (
            select(UserSkill.skill_id, func.count(distinct(UserSkill.user_id)))
            .join(StudentProfile, StudentProfile.user_id == UserSkill.user_id)
            .where(StudentProfile.institution_id == institution_id)
            .group_by(UserSkill.skill_id)
        )
        return {row[0]: row[1] for row in self.db.execute(stmt).all()}

    def get_skill_names(self, skill_ids: list[uuid.UUID]) -> dict[uuid.UUID, str]:
        if not skill_ids:
            return {}
        stmt = select(Skill.id, Skill.name).where(Skill.id.in_(skill_ids))
        return {row[0]: row[1] for row in self.db.execute(stmt).all()}
