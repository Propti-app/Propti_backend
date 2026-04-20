from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Landlord
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import os

load_dotenv()
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

security = HTTPBearer()


def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verifies Firebase ID token"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_landlord_id(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> int:
    """Returns landlord_id - BACKWARDS COMPATIBLE"""
    firebase_uid = token_data["uid"]
    
    landlord = db.query(Landlord).filter(
        Landlord.firebase_uid == firebase_uid
    ).first()
    
    if not landlord:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not synced. Call /auth/sync first"
        )
    
    return landlord.landlord_id


def get_current_landlord(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> Landlord:
    """Returns full Landlord object"""
    firebase_uid = token_data["uid"]
    
    landlord = db.query(Landlord).filter(
        Landlord.firebase_uid == firebase_uid
    ).first()
    
    if not landlord:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not synced. Call /auth/sync first"
        )
    
    return landlord


