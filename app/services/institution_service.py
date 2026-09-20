import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.institution_repository import InstitutionRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.institution import SkillGapItem, SkillGapReportOut


class InstitutionService:
    """
    Flow C: Academician dashboard skill-gap report.

    gap_score(skill) = demand_count (live opportunities requiring it, across
    every registered organization) - supply_count (this institution's
    students who already have it). Reuses the same tables Flows A/B already
    populate — no curriculum entity, per Section 6.1 scoping.
    """

    def __init__(self, db: Session):
        self.db = db
        self.institutions = InstitutionRepository(db)
        self.organizations = OrganizationRepository(db)

    def get_skill_gap_report(self, institution_id: uuid.UUID) -> SkillGapReportOut:
        institution = self.organizations.get_by_id(institution_id)
        if institution is None or institution.organization_type != "INSTITUTION":
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Institution not found.")

        demand = self.institutions.demand_by_skill()
        supply = self.institutions.supply_by_skill(institution_id)
        all_skill_ids = list(set(demand.keys()) | set(supply.keys()))
        skill_names = self.institutions.get_skill_names(all_skill_ids)

        gaps = [
            SkillGapItem(
                skill_id=skill_id,
                skill_name=skill_names.get(skill_id, str(skill_id)),
                demand_count=demand.get(skill_id, 0),
                supply_count=supply.get(skill_id, 0),
                gap_score=demand.get(skill_id, 0) - supply.get(skill_id, 0),
            )
            for skill_id in all_skill_ids
        ]
        gaps.sort(key=lambda g: g.gap_score, reverse=True)

        return SkillGapReportOut(
            institution_id=institution.id,
            institution_name=institution.name,
            total_students=self.institutions.count_students(institution_id),
            gaps=gaps,
        )
