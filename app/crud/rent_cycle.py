from sqlalchemy.orm import Session
from ..models import RentCycle, Room, Tenant
from ..schemas import RentCycleCreate
import uuid

def create_rent_cycle(db: Session, rent_cycle: RentCycleCreate):
    db_rent_cycle = RentCycle(**rent_cycle.dict())
    db.add(db_rent_cycle)
    db.commit()
    db.refresh(db_rent_cycle)
    return db_rent_cycle

def get_rent_cycles(db: Session, room_id: int, skip: int = 0, limit: int = 100):
    return db.query(RentCycle).filter(RentCycle.room_id == room_id).offset(skip).limit(limit).all()