from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrganizationOut

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationOut])
def list_organizations(
    organization_type: str | None = Query(default=None, description="Filter: INSTITUTION | INDUSTRY"),
    db: Session = Depends(get_db),
):
    """
    Lookup endpoint — mainly so a Postman/frontend flow can find an
    institution_id (for the Flow C skill-gap report) or organization_id
    without querying Postgres directly.
    """
    return OrganizationRepository(db).list_by_type(organization_type)