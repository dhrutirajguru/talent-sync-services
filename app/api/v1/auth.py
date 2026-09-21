from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import MeOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MeOut, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register(payload)
    return MeOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role_codes=user.role_codes,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService(db).login(payload.email, payload.password)
    return TokenResponse(access_token=token)
