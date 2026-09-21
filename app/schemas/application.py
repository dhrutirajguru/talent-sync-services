import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    opportunity_id: uuid.UUID
    cover_letter: str | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    opportunity_id: uuid.UUID
    opportunity_title: str
    organization_name: str
    applicant_user_id: uuid.UUID
    applicant_name: str
    status: str
    applied_at: datetime | None = None
