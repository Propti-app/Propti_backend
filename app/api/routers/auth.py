from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, crud
from ...database import get_db
from ...models import Landlord
from app import models

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.LandlordResponse)
def register_landlord(landlord: schemas.LandlordCreate, db: Session = Depends(get_db)):
    # Check if email/phone exists
    existing = db.query(models.Landlord).filter(
        (models.Landlord.email == landlord.email) | 
        (models.Landlord.phone_number == landlord.phone_number)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or phone number already registered")
    return crud.create_landlord(db, landlord)



# @router.post("/register", response_model=schemas.LandlordResponse)
# def register_landlord(landlord: schemas.LandlordCreate, db: Session = Depends(get_db)):
#     # Check if email/phone exists
#     existing = db.query(Landlord).filter(
#         (Landlord.email == landlord.email) | 
#         (Landlord.phone_number == landlord.phone_number)
#     ).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email or phone number already registered")
#     return crud.create_landlord(db, landlord)

@router.post("/login")
def login(email: str, password: str):
    # Note: Firebase Auth handles login on client-side (Flutter), returns token
    # This endpoint is a placeholder for server-side validation if needed
    return {"message": "Use Firebase Auth to get token, then pass to protected endpoints"}
