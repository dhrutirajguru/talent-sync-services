from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import MeOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=MeOut)
def get_me(current_user: User = Depends(get_current_user)):
    return MeOut(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role_codes=current_user.role_codes,
    )
