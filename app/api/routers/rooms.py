from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, crud, models
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=schemas.RoomResponse)
def create_room(
    room: schemas.RoomCreate,
    property_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    # Verify property belongs to landlord
    property = db.query(models.Property).filter(
        models.Property.property_id == property_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not property:
        raise HTTPException(status_code=403, detail="Not authorized to add room to this property")
    return crud.create_room(db, room, property_id)

@router.get("/", response_model=list[schemas.RoomResponse])
def get_rooms(
    property_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    property = db.query(models.Property).filter(
        models.Property.property_id == property_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not property:
        raise HTTPException(status_code=403, detail="Not authorized to view rooms")
    return crud.get_rooms(db, property_id, skip, limit)

@router.put("/{room_id}", response_model=schemas.RoomResponse)
def update_room(
    room_id: int,
    room: schemas.RoomCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    db_room = crud.update_room(db, room_id, room)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    property = db.query(models.Property).filter(
        models.Property.property_id == db_room.property_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not property:
        raise HTTPException(status_code=403, detail="Not authorized to update this room")
    return db_room








# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ... import schemas, crud
# from ...database import get_db
# from ...utils.auth import get_current_landlord_id

# router = APIRouter(prefix="/rooms", tags=["Rooms"])

# @router.post("/", response_model=schemas.RoomResponse)
# def create_room(
#     room: schemas.RoomCreate,
#     property_id: int,
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     # Verify property belongs to landlord
#     property = db.query(crud.models.Property).filter(
#         crud.models.Property.property_id == property_id,
#         crud.models.Property.landlord_id == landlord_id
#     ).first()
#     if not property:
#         raise HTTPException(status_code=403, detail="Not authorized to add room to this property")
#     return crud.create_room(db, room, property_id)

# @router.get("/", response_model=list[schemas.RoomResponse])
# def get_rooms(
#     property_id: int,
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db),
#     skip: int = 0,
#     limit: int = 100
# ):
#     property = db.query(crud.models.Property).filter(
#         crud.models.Property.property_id == property_id,
#         crud.models.Property.landlord_id == landlord_id
#     ).first()
#     if not property:
#         raise HTTPException(status_code=403, detail="Not authorized to view rooms")
#     return crud.get_rooms(db, property_id, skip, limit)

# @router.put("/{room_id}", response_model=schemas.RoomResponse)
# def update_room(
#     room_id: int,
#     room: schemas.RoomCreate,
#     landlord_id: int = Depends(get_current_landlord_id),
#     db: Session = Depends(get_db)
# ):
#     db_room = crud.update_room(db, room_id, room)
#     if not db_room:
#         raise HTTPException(status_code=404, detail="Room not found")
#     property = db.query(crud.models.Property).filter(
#         crud.models.Property.property_id == db_room.property_id,
#         crud.models.Property.landlord_id == landlord_id
#     ).first()
#     if not property:
#         raise HTTPException(status_code=403, detail="Not authorized to update this room")
#     return db_room