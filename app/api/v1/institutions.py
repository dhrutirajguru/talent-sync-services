from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.institution import SkillGapReportOut
from app.services.institution_service import InstitutionService

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("/{institution_id}/skill-gap", response_model=SkillGapReportOut)
def get_skill_gap_report(institution_id: str, db: Session = Depends(get_db)):
    """
    Flow C: aggregate demand (skills required across every live opportunity)
    vs. supply (skills this institution's students already have).
    Left without a role guard for demo simplicity; wire it behind
    require_role("ACADEMICIAN") plus profile-derived institution_id once
    academician login is fully threaded through the frontend.
    """
    return InstitutionService(db).get_skill_gap_report(institution_id)
