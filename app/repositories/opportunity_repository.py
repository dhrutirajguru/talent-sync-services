import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.opportunity import Opportunity, OpportunitySkill


class OpportunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def _with_relations(self, stmt):
        return stmt.options(
            selectinload(Opportunity.organization),
            selectinload(Opportunity.required_skills).selectinload(OpportunitySkill.skill),
        )

    def create(
        self,
        *,
        organization_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        data: dict,
        required_skills: list[dict],
    ) -> Opportunity:
        opportunity = Opportunity(
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            status="PUBLISHED",
            published_at=datetime.now(timezone.utc),
            **data,
        )
        self.db.add(opportunity)
        self.db.flush()

        for skill in required_skills:
            self.db.add(
                OpportunitySkill(
                    opportunity_id=opportunity.id,
                    skill_id=skill["skill_id"],
                    required_level=skill.get("required_level"),
                    importance=skill.get("importance", "MEDIUM"),
                    required=skill.get("required", True),
                )
            )
        self.db.flush()
        return self.get_by_id(opportunity.id)  # reload with relations populated

    def get_by_id(self, opportunity_id: uuid.UUID) -> Opportunity | None:
        stmt = self._with_relations(select(Opportunity).where(Opportunity.id == opportunity_id))
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_organization(self, organization_id: uuid.UUID) -> list[Opportunity]:
        stmt = self._with_relations(
            select(Opportunity).where(Opportunity.organization_id == organization_id)
        ).order_by(Opportunity.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_published(self) -> list[Opportunity]:
        """All live opportunities across every registered organization — the
        pool a student's recommendations are matched against (Flow A)."""
        stmt = self._with_relations(
            select(Opportunity).where(Opportunity.status == "PUBLISHED")
        ).order_by(Opportunity.published_at.desc())
        return list(self.db.execute(stmt).scalars().all())
