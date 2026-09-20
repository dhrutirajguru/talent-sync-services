import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.schemas.application import ApplicationCreate, ApplicationOut


def _to_application_out(application: Application) -> ApplicationOut:
    applicant = application.applicant
    name = applicant.first_name + (f" {applicant.last_name}" if applicant.last_name else "")
    return ApplicationOut(
        id=application.id,
        opportunity_id=application.opportunity_id,
        opportunity_title=application.opportunity.title,
        applicant_user_id=application.applicant_user_id,
        applicant_name=name,
        status=application.status,
        applied_at=application.applied_at,
    )


class ApplicationService:
    def __init__(self, db: Session):
        self.db = db
        self.applications = ApplicationRepository(db)
        self.opportunities = OpportunityRepository(db)

    def apply(self, *, student_user_id: uuid.UUID, payload: ApplicationCreate) -> ApplicationOut:
        opportunity = self.opportunities.get_by_id(payload.opportunity_id)
        if opportunity is None or opportunity.status != "PUBLISHED":
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found or no longer open.")

        if self.applications.exists_for_user_and_opportunity(payload.opportunity_id, student_user_id):
            raise HTTPException(status.HTTP_409_CONFLICT, "You have already applied to this opportunity.")

        application = self.applications.create(
            opportunity_id=payload.opportunity_id,
            applicant_user_id=student_user_id,
            cover_letter=payload.cover_letter,
        )
        self.db.commit()
        return _to_application_out(application)

    def list_for_opportunity(self, opportunity_id: uuid.UUID) -> list[ApplicationOut]:
        return [_to_application_out(a) for a in self.applications.list_by_opportunity(opportunity_id)]

    def list_for_student(self, student_user_id: uuid.UUID) -> list[ApplicationOut]:
        return [_to_application_out(a) for a in self.applications.list_by_student(student_user_id)]
