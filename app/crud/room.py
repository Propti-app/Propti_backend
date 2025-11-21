from sqlalchemy.orm import Session
from ..models import Room
from ..schemas import RoomCreate

def create_room(db: Session, room: RoomCreate, property_id: int):
    db_room = Room(**room.dict(), property_id=property_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_rooms(db: Session, property_id: int, skip: int = 0, limit: int = 100):
    return db.query(Room).filter(Room.property_id == property_id).offset(skip).limit(limit).all()

def update_room(db: Session, room_id: int, room: RoomCreate):
    db_room = db.query(Room).filter(Room.room_id == room_id).first()
    if not db_room:
        return None
    for key, value in room.dict().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return db_room