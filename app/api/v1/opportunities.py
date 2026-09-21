from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.user import User
from app.repositories.organization_repository import ProfileRepository
from app.schemas.opportunity import (
    CandidateMatchOut,
    OpportunityCreate,
    OpportunityMatchOut,
    OpportunityOut,
)
from app.services.opportunity_service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _industry_organization_id(current_user: User, db: Session):
    profile = ProfileRepository(db).get_industry_profile(current_user.id)
    if profile is None or profile.organization_id is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Your industry profile has no organization linked yet.",
        )
    return profile.organization_id


@router.post("", response_model=OpportunityOut, status_code=201)
def create_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(require_role("INDUSTRY")),
    db: Session = Depends(get_db),
):
    org_id = _industry_organization_id(current_user, db)
    return OpportunityService(db).create_opportunity(
        organization_id=org_id, created_by_user_id=current_user.id, payload=payload
    )


@router.get("", response_model=list[OpportunityOut])
def list_my_organization_opportunities(
    current_user: User = Depends(require_role("INDUSTRY")),
    db: Session = Depends(get_db),
):
    """Industry: postings belonging to my own organization."""
    org_id = _industry_organization_id(current_user, db)
    return OpportunityService(db).list_for_organization(org_id)


@router.get("/recommended", response_model=list[OpportunityMatchOut])
def get_recommended_opportunities(
    current_user: User = Depends(require_role("STUDENT")),
    db: Session = Depends(get_db),
):
    """Student: ranked matches across every registered organization (Flow A)."""
    return OpportunityService(db).list_recommended_for_student(current_user.id)


@router.get("/{opportunity_id}/candidates", response_model=list[CandidateMatchOut])
def get_ranked_candidates(
    opportunity_id: str,
    current_user: User = Depends(require_role("INDUSTRY")),
    db: Session = Depends(get_db),
):
    """Industry: ranked candidates for one of my postings (Flow B)."""
    org_id = _industry_organization_id(current_user, db)
    return OpportunityService(db).list_candidates_for_opportunity(opportunity_id, org_id)
