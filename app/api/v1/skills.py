from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.skill import SkillOut, UserSkillOut, UserSkillsUpdateRequest
from app.services.skill_service import SkillService

router = APIRouter(tags=["skills"])


@router.get("/skills", response_model=list[SkillOut])
def list_skill_catalog(db: Session = Depends(get_db)):
    """Full skill catalog — used to populate profile-edit and post-opportunity dropdowns."""
    return SkillService(db).list_catalog()


@router.get("/users/me/skills", response_model=list[UserSkillOut])
def get_my_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SkillService(db).get_user_skills(current_user.id)


@router.put("/users/me/skills", response_model=list[UserSkillOut])
def update_my_skills(
    payload: UserSkillsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full-replace update — the profile-edit screen sends the complete current skill set."""
    return SkillService(db).update_user_skills(current_user.id, payload)
