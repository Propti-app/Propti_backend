from sqlalchemy.orm import Session
from ..models import Property
from ..schemas import PropertyCreate

def create_property(db: Session, property: PropertyCreate, landlord_id: int):
    db_property = Property(**property.dict(), landlord_id=landlord_id)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property
