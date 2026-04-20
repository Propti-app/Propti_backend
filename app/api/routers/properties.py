from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from ... import schemas, crud
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.post("/", response_model=schemas.PropertyResponse)
def create_property(
    property: schemas.PropertyCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    return crud.create_property(db, property, landlord_id)

# Added enpoint to Get all properties for landlord
@router.get("/", response_model=list[schemas.PropertyResponse])
def get_properties(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    properties = db.query(models.Property).filter(
        models.Property.landlord_id == landlord_id,
        models.Property.is_active == True
    ).offset(skip).limit(limit).all()
    return properties





