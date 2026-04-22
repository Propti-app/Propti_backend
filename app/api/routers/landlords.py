from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ... import schemas, crud, models
from ...database import get_db
from ...utils.auth import get_current_landlord, get_current_landlord_id

router = APIRouter(prefix="/landlords", tags=["Landlords"])


# ── Schemas local to this router ──────────────────────────────────────────────

class FcmTokenUpdate(BaseModel):
    fcm_token: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=schemas.LandlordResponse)
def create_landlord(landlord: schemas.LandlordCreate, db: Session = Depends(get_db)):
    return crud.create_landlord(db, landlord)


@router.put("/settings", response_model=schemas.LandlordResponse)
def update_settings(
    settings: schemas.LandlordSettingsUpdate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
):
    db_landlord = crud.update_landlord_settings(db, landlord_id, settings)
    if not db_landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")
    return db_landlord


@router.get("/settings", response_model=schemas.LandlordResponse)
def get_settings(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
):
    db_landlord = crud.get_landlord_settings(db, landlord_id)
    if not db_landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")
    return db_landlord


@router.patch("/fcm-token")
def update_fcm_token(
    body: FcmTokenUpdate,
    landlord: models.Landlord = Depends(get_current_landlord),
    db: Session = Depends(get_db),
):
    """
    Flutter calls PATCH /landlords/fcm-token after Firebase Messaging init.
    Stores the device push token so the backend can send FCM notifications.
    """
    landlord.fcm_token = body.fcm_token
    db.commit()
    return {"success": True}
















