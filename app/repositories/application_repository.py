import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.application import Application
from app.models.opportunity import Opportunity
from app.models.user import User


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def _with_relations(self, stmt):
        return stmt.options(
            selectinload(Application.opportunity),
            selectinload(Application.applicant),
        )

    def create(self, *, opportunity_id: uuid.UUID, applicant_user_id: uuid.UUID, cover_letter: str | None) -> Application:
        application = Application(
            opportunity_id=opportunity_id,
            applicant_user_id=applicant_user_id,
            cover_letter=cover_letter,
            applied_at=datetime.now(timezone.utc),
            status="SUBMITTED",
            status_updated_at=datetime.now(timezone.utc),
        )
        self.db.add(application)
        self.db.flush()
        return self.get_by_id(application.id)

    def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        stmt = self._with_relations(select(Application).where(Application.id == application_id))
        return self.db.execute(stmt).scalar_one_or_none()

    def exists_for_user_and_opportunity(self, opportunity_id: uuid.UUID, applicant_user_id: uuid.UUID) -> bool:
        stmt = select(Application.id).where(
            Application.opportunity_id == opportunity_id,
            Application.applicant_user_id == applicant_user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def list_by_opportunity(self, opportunity_id: uuid.UUID) -> list[Application]:
        stmt = self._with_relations(
            select(Application).where(Application.opportunity_id == opportunity_id)
        ).order_by(Application.applied_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_applicant_ids_for_opportunity(self, opportunity_id: uuid.UUID) -> set[uuid.UUID]:
        stmt = select(Application.applicant_user_id).where(Application.opportunity_id == opportunity_id)
        return set(self.db.execute(stmt).scalars().all())

    def list_by_student(self, applicant_user_id: uuid.UUID) -> list[Application]:
        stmt = self._with_relations(
            select(Application).where(Application.applicant_user_id == applicant_user_id)
        ).order_by(Application.applied_at.desc())
        return list(self.db.execute(stmt).scalars().all())
