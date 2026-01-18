# app/api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, models
from ...database import get_db
from ...utils.auth import verify_firebase_token, get_current_landlord

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/sync", response_model=schemas.LandlordResponse)
def sync_landlord(
    landlord_data: schemas.LandlordSync,
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Sync Firebase user to database"""
    firebase_uid = token_data["uid"]
    firebase_email = token_data.get("email")
    
    if firebase_email != landlord_data.email:
        raise HTTPException(status_code=400, detail="Email mismatch")
    
    # Check if already synced
    existing = db.query(models.Landlord).filter(
        models.Landlord.firebase_uid == firebase_uid
    ).first()
    
    if existing:
        return existing
    
    # Check conflicts
    conflict = db.query(models.Landlord).filter(
        (models.Landlord.email == landlord_data.email) | 
        (models.Landlord.phone_number == landlord_data.phone_number)
    ).first()
    
    if conflict:
        raise HTTPException(status_code=400, detail="Email or phone already registered")
    
    # Create new landlord
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
    """Get current user profile"""
    return current_landlord




# # app/api/routers/auth.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ... import schemas, models  # This goes up to 'app' package
# from ...database import get_db
# from ...utils.auth import verify_firebase_token, get_current_landlord

# router = APIRouter(prefix="/auth", tags=["Authentication"])


# @router.post("/sync", response_model=schemas.LandlordResponse)
# def sync_landlord(
#     landlord_data: schemas.LandlordSync,
#     token_data: dict = Depends(verify_firebase_token),
#     db: Session = Depends(get_db)
# ):
#     """Sync Firebase user to database"""
#     firebase_uid = token_data["uid"]
#     firebase_email = token_data.get("email")
    
#     if firebase_email != landlord_data.email:
#         raise HTTPException(status_code=400, detail="Email mismatch")
    
#     # Check if already synced
#     existing = db.query(models.Landlord).filter(
#         models.Landlord.firebase_uid == firebase_uid
#     ).first()
    
#     if existing:
#         return existing
    
#     # Check conflicts
#     conflict = db.query(models.Landlord).filter(
#         (models.Landlord.email == landlord_data.email) | 
#         (models.Landlord.phone_number == landlord_data.phone_number)
#     ).first()
    
#     if conflict:
#         raise HTTPException(status_code=400, detail="Email or phone already registered")
    
#     # Create new landlord
#     new_landlord = models.Landlord(
#         firebase_uid=firebase_uid,
#         email=landlord_data.email,
#         name=landlord_data.full_name,
#         phone_number=landlord_data.phone_number,
#         password_hash=None
#     )
    
#     db.add(new_landlord)
#     db.commit()
#     db.refresh(new_landlord)
    
#     return new_landlord


# @router.get("/status")
# def check_sync_status(
#     token_data: dict = Depends(verify_firebase_token),
#     db: Session = Depends(get_db)
# ):
#     """Check if Firebase user exists in database"""
#     firebase_uid = token_data["uid"]
    
#     landlord = db.query(models.Landlord).filter(
#         models.Landlord.firebase_uid == firebase_uid
#     ).first()
    
#     return {
#         "is_synced": landlord is not None,
#         "landlord_id": landlord.landlord_id if landlord else None,
#         "email": token_data.get("email")
#     }


# @router.get("/me", response_model=schemas.LandlordResponse)
# def get_current_user(
#     current_landlord: models.Landlord = Depends(get_current_landlord)
# ):
#     """Get current user profile"""
#     return current_landlord