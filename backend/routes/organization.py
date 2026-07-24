import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, Organization
from auth import get_current_user

router = APIRouter()


class OrgUpdate(BaseModel):
    name: str | None = None
    primary_color: str | None = None
    font_family: str | None = None
    logo_url: str | None = None


@router.get("/")
def get_organization(
    user: User = Depends(get_current_user),
):
    org = user.organization
    if not org:
        raise HTTPException(404, "No organization")
    return {
        "id": org.id,
        "name": org.name,
        "logo_url": org.logo_url,
        "primary_color": org.primary_color,
        "font_family": org.font_family,
    }


@router.put("/")
def update_organization(
    data: OrgUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = user.organization
    if not org:
        raise HTTPException(404, "No organization")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(org, k, v)
    db.commit()
    db.refresh(org)
    return {
        "id": org.id,
        "name": org.name,
        "logo_url": org.logo_url,
        "primary_color": org.primary_color,
        "font_family": org.font_family,
    }
