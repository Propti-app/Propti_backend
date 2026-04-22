from sqlalchemy.orm import Session
from app.models import Property, PropertyType
from app.schemas import PropertyCreate


def _to_property_type(val: str | None) -> PropertyType:
    """Convert string 'hostel'/'residential' to PropertyType enum safely."""
    if val == "residential":
        return PropertyType.RESIDENTIAL
    return PropertyType.HOSTEL  # default


def create_property(db: Session, property: PropertyCreate, landlord_id: int):
    db_property = Property(
        landlord_id=landlord_id,
        name=property.name,
        location=property.location,
        property_type=_to_property_type(property.property_type),
        photo=property.photo,
        photo_urls=[],
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def get_properties(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    return db.query(Property).filter(
        Property.landlord_id == landlord_id,
        Property.is_active == True,
    ).offset(skip).limit(limit).all()


def update_property(db: Session, property_id: int, landlord_id: int, data: dict):
    prop = db.query(Property).filter(
        Property.property_id == property_id,
        Property.landlord_id == landlord_id,
    ).first()
    if not prop:
        return None
    for key, value in data.items():
        if value is None:
            continue
        if key == "property_type":
            setattr(prop, key, _to_property_type(value))
        elif hasattr(prop, key):
            setattr(prop, key, value)
    db.commit()
    db.refresh(prop)
    return prop


def deactivate_property(db: Session, property_id: int, landlord_id: int):
    prop = db.query(Property).filter(
        Property.property_id == property_id,
        Property.landlord_id == landlord_id,
    ).first()
    if not prop:
        return None
    prop.is_active = False
    db.commit()
    db.refresh(prop)
    return prop







