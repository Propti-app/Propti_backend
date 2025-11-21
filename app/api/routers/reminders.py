from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ... import crud
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.post("/schedule")
def schedule_reminders(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    crud.schedule_reminders(db)
    return {"message": "Reminders scheduled"}

