from sqlalchemy.orm import Session
from ..models import Landlord
from ..schemas import LandlordCreate, LandlordSettingsUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_landlord(db: Session, landlord: LandlordCreate):
    hashed_password = pwd_context.hash(landlord.password)
    db_landlord = Landlord(
        email=landlord.email,
        phone_number=landlord.phone_number,
        name=landlord.name,
        password_hash=hashed_password
    )
    db.add(db_landlord)
    db.commit()
    db.refresh(db_landlord)
    return db_landlord

def update_landlord_settings(db: Session, landlord_id: int, settings: LandlordSettingsUpdate):
    db_landlord = db.query(Landlord).filter(Landlord.landlord_id == landlord_id).first()
    if not db_landlord:
        return None
    db_landlord.settings = settings.dict()
    db.commit()
    db.refresh(db_landlord)
    return db_landlord

def get_landlord_settings(db: Session, landlord_id: int):
    return db.query(Landlord).filter(Landlord.landlord_id == landlord_id).first()