from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import User
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.organization_repository import ProfileRepository
from app.schemas.application import ApplicationCreate, ApplicationOut
from app.services.application_service import ApplicationService

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationOut, status_code=201)
def apply_to_opportunity(
    payload: ApplicationCreate,
    current_user: User = Depends(require_role("STUDENT")),
    db: Session = Depends(get_db),
):
    """The Flow A -> Flow B bridge: a student applies to a matched opportunity."""
    return ApplicationService(db).apply(student_user_id=current_user.id, payload=payload)


@router.get("/opportunities/{opportunity_id}/applications", response_model=list[ApplicationOut])
def list_applications_for_opportunity(
    opportunity_id: str,
    current_user: User = Depends(require_role("INDUSTRY")),
    db: Session = Depends(get_db),
):
    """Industry: applicants who have applied to one of my postings."""
    org_profile = ProfileRepository(db).get_industry_profile(current_user.id)
    opportunity = OpportunityRepository(db).get_by_id(opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found.")
    if org_profile is None or opportunity.organization_id != org_profile.organization_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This opportunity belongs to a different organization.")

    return ApplicationService(db).list_for_opportunity(opportunity_id)
