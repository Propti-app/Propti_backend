from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, crud, models
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/rent-cycles", tags=["Rent Cycles"])

@router.post("/", response_model=schemas.RentCycleResponse)
def create_rent_cycle(
    rent_cycle: schemas.RentCycleCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    # Verify room belongs to landlord
    room = db.query(models.Room).join(
        models.Property, models.Room.property_id == models.Property.property_id
    ).filter(
        models.Room.room_id == rent_cycle.room_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized to create rent cycle for this room")
    # Verify tenant (if provided) is assigned to the room
    if rent_cycle.tenant_id:
        tenant = db.query(models.Tenant).filter(
            models.Tenant.tenant_id == rent_cycle.tenant_id,
            models.Tenant.assigned_room_id == rent_cycle.room_id
        ).first()
        if not tenant:
            raise HTTPException(status_code=400, detail="Tenant not assigned to this room")
    return crud.create_rent_cycle(db, rent_cycle)

@router.get("/room/{room_id}", response_model=list[schemas.RentCycleResponse])
def get_rent_cycles(
    room_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    room = db.query(models.Room).join(
        models.Property, models.Room.property_id == models.Property.property_id
    ).filter(
        models.Room.room_id == room_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized to view rent cycles")
    return crud.get_rent_cycles(db, room_id, skip, limit)