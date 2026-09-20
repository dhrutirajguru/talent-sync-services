from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str | None = None
    role_code: str = Field(description="STUDENT | ACADEMICIAN | INDUSTRY")
    # Optional linkage at signup time — keeps the demo seed/signup path simple.
    # Student -> institution org id, Academician -> institution org id,
    # Industry -> employer org id.
    organization_id: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
