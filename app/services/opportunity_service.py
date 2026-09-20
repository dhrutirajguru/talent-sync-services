import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.repositories.application_repository import ApplicationRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.skill_repository import SkillRepository
from app.repositories.user_repository import UserRepository
from app.schemas.opportunity import (
    CandidateMatchOut,
    OpportunityCreate,
    OpportunityMatchOut,
    OpportunityOut,
    OpportunitySkillOut,
)
from app.services.matching_service import compute_match, matched_and_missing


def _to_opportunity_out(opportunity: Opportunity) -> OpportunityOut:
    return OpportunityOut(
        id=opportunity.id,
        organization_id=opportunity.organization_id,
        organization_name=opportunity.organization.name,
        title=opportunity.title,
        opportunity_type=opportunity.opportunity_type,
        description=opportunity.description,
        location=opportunity.location,
        work_mode=opportunity.work_mode,
        status=opportunity.status,
        required_skills=[
            OpportunitySkillOut(
                skill_id=req.skill_id,
                skill_name=req.skill.name,
                required_level=req.required_level,
                importance=req.importance,
                required=req.required,
            )
            for req in opportunity.required_skills
        ],
    )


class OpportunityService:
    def __init__(self, db: Session):
        self.db = db
        self.opportunities = OpportunityRepository(db)
        self.skills = SkillRepository(db)
        self.applications = ApplicationRepository(db)
        self.users = UserRepository(db)

    # ---- Flow B: Industry posts an opportunity ----
    def create_opportunity(self, *, organization_id: uuid.UUID, created_by_user_id: uuid.UUID, payload: OpportunityCreate) -> OpportunityOut:
        skill_ids = [s.skill_id for s in payload.required_skills]
        found_skills = {s.id for s in self.skills.get_by_ids(skill_ids)}
        unknown = set(skill_ids) - found_skills
        if unknown:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown skill id(s): {unknown}")

        data = payload.model_dump(exclude={"required_skills"})
        opportunity = self.opportunities.create(
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            data=data,
            required_skills=[s.model_dump() for s in payload.required_skills],
        )
        self.db.commit()
        return _to_opportunity_out(self.opportunities.get_by_id(opportunity.id))

    def list_for_organization(self, organization_id: uuid.UUID) -> list[OpportunityOut]:
        return [_to_opportunity_out(o) for o in self.opportunities.list_by_organization(organization_id)]

    # ---- Flow A: Student sees ranked matches across every organization ----
    def list_recommended_for_student(self, student_user_id: uuid.UUID) -> list[OpportunityMatchOut]:
        possessed = {row.skill_id for row in self.skills.get_user_skills(student_user_id)}
        skill_names = {s.id: s.name for s in self.skills.list_all()}

        results: list[OpportunityMatchOut] = []
        for opp in self.opportunities.list_published():
            required_ids = {req.skill_id for req in opp.required_skills}
            score = compute_match(required_ids, possessed)
            matched_names, missing_names = matched_and_missing(required_ids, possessed, skill_names)
            base = _to_opportunity_out(opp)
            results.append(
                OpportunityMatchOut(
                    **base.model_dump(),
                    match_score=score,
                    matched_skill_names=matched_names,
                    missing_skill_names=missing_names,
                )
            )
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results

    # ---- Flow B (continued): Industry sees ranked candidates for one posting ----
    def list_candidates_for_opportunity(self, opportunity_id: uuid.UUID) -> list[CandidateMatchOut]:
        opportunity = self.opportunities.get_by_id(opportunity_id)
        if opportunity is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found.")

        required_ids = {req.skill_id for req in opportunity.required_skills}
        skill_names = {s.id: s.name for s in self.skills.list_all()}
        applied_user_ids = self.applications.list_applicant_ids_for_opportunity(opportunity_id)

        # Demo-scale simplicity: one query per student for their skills (small
        # seeded dataset). Batch this into a single joined query if the
        # candidate pool grows beyond demo size.
        students = self.users.list_by_role("STUDENT")
        results: list[CandidateMatchOut] = []
        for student in students:
            possessed = {row.skill_id for row in self.skills.get_user_skills(student.id)}
            score = compute_match(required_ids, possessed)
            matched_names, missing_names = matched_and_missing(required_ids, possessed, skill_names)
            results.append(
                CandidateMatchOut(
                    user_id=student.id,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.email,
                    match_score=score,
                    matched_skill_names=matched_names,
                    missing_skill_names=missing_names,
                    has_applied=student.id in applied_user_ids,
                )
            )
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results
