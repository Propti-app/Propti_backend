from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Landlord
import firebase_admin
from firebase_admin import credentials, auth
import os
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Initialize Firebase Admin SDK safely
if not firebase_admin._apps:
    firebase_cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if not firebase_cred_json:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not set")

    cred = credentials.Certificate(json.loads(firebase_cred_json))
    firebase_admin.initialize_app(cred)


def get_current_landlord_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        landlord = db.query(Landlord).filter(Landlord.email == email).first()

        if not landlord:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Landlord not registered in system",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return landlord.landlord_id

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )












# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models import Landlord
# import firebase_admin
# from firebase_admin import credentials, auth
# from dotenv import load_dotenv
# import os

# load_dotenv()
# FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate(FIREBASE_CRED_PATH)
# firebase_admin.initialize_app(cred)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# def get_current_landlord_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         decoded_token = auth.verify_id_token(token)
#         email = decoded_token["email"]
#         landlord = db.query(Landlord).filter(Landlord.email == email).first()
#         if not landlord:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Landlord not registered in system",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return landlord.landlord_id
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )










# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# import firebase_admin
# from firebase_admin import credentials, auth
# from dotenv import load_dotenv
# import os

# load_dotenv()
# FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate(FIREBASE_CRED_PATH)
# firebase_admin.initialize_app(cred)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# def get_current_landlord_id(token: str = Depends(oauth2_scheme)):
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return decoded_token["uid"]  # Firebase UID (we'll map to landlord_id later)
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
