from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..utils.auth import verify_firebase_token, get_current_landlord

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/sync", response_model=schemas.LandlordResponse)
def sync_landlord(
    landlord_data: schemas.LandlordSync,
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """
    Syncs Firebase user to database.
    Called once after Firebase registration in Flutter.
    """
    firebase_uid = token_data["uid"]
    firebase_email = token_data.get("email")
    
    # Verify email matches
    if firebase_email != landlord_data.email:
        raise HTTPException(
            status_code=400,
            detail="Email mismatch between token and request"
        )
    
    # Check if already synced
    existing = db.query(models.Landlord).filter(
        models.Landlord.firebase_uid == firebase_uid
    ).first()
    
    if existing:
        return existing
    
    # Check for conflicts
    conflict = db.query(models.Landlord).filter(
        (models.Landlord.email == landlord_data.email) | 
        (models.Landlord.phone_number == landlord_data.phone_number)
    ).first()
    
    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Email or phone number already registered"
        )
    
    # Create landlord record
    new_landlord = models.Landlord(
        firebase_uid=firebase_uid,
        email=landlord_data.email,
        name=landlord_data.full_name,
        phone_number=landlord_data.phone_number,
        password_hash=None
    )
    
    db.add(new_landlord)
    db.commit()
    db.refresh(new_landlord)
    
    return new_landlord


@router.get("/status")
def check_sync_status(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Check if Firebase user exists in database"""
    firebase_uid = token_data["uid"]
    
    landlord = db.query(models.Landlord).filter(
        models.Landlord.firebase_uid == firebase_uid
    ).first()
    
    return {
        "is_synced": landlord is not None,
        "landlord_id": landlord.landlord_id if landlord else None,
        "email": token_data.get("email"),
        "firebase_uid": firebase_uid
    }


@router.get("/me", response_model=schemas.LandlordResponse)
def get_current_user(
    current_landlord: models.Landlord = Depends(get_current_landlord)
):
    """Returns current authenticated landlord's profile"""
    return current_landlord




# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ... import schemas, crud
# from ...database import get_db
# from ...models import Landlord
# from app import models

# router = APIRouter(prefix="/auth", tags=["Authentication"])


# @router.post("/register", response_model=schemas.LandlordResponse)
# def register_landlord(landlord: schemas.LandlordCreate, db: Session = Depends(get_db)):
#     # Check if email/phone exists
#     existing = db.query(models.Landlord).filter(
#         (models.Landlord.email == landlord.email) | 
#         (models.Landlord.phone_number == landlord.phone_number)
#     ).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email or phone number already registered")
#     return crud.create_landlord(db, landlord)



# # @router.post("/register", response_model=schemas.LandlordResponse)
# # def register_landlord(landlord: schemas.LandlordCreate, db: Session = Depends(get_db)):
# #     # Check if email/phone exists
# #     existing = db.query(Landlord).filter(
# #         (Landlord.email == landlord.email) | 
# #         (Landlord.phone_number == landlord.phone_number)
# #     ).first()
# #     if existing:
# #         raise HTTPException(status_code=400, detail="Email or phone number already registered")
# #     return crud.create_landlord(db, landlord)

# @router.post("/login")
# def login(email: str, password: str):
#     # Note: Firebase Auth handles login on client-side (Flutter), returns token
#     # This endpoint is a placeholder for server-side validation if needed
#     return {"message": "Use Firebase Auth to get token, then pass to protected endpoints"}
