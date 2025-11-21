from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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










# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ...crud import property as crud_property  # Import with alias to avoid conflict
# from ... import schemas
# from ...database import get_db

# router = APIRouter(prefix="/properties", tags=["Properties"])

# @router.post("/", response_model=schemas.PropertyResponse)
# def create_property(property: schemas.PropertyCreate, landlord_id: int = 1, db: Session = Depends(get_db)):
#     return crud_property.create_property(db, property, landlord_id)