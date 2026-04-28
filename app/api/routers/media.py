# app/api/routers/media.py
"""
Media upload endpoints.
The backend never rejects based on content_type when it could be octet-stream
(camera images on iOS/Android sometimes arrive as octet-stream).
Instead we validate by checking the file magic bytes for images, and trust
the Flutter client's explicit contentType hint when present.
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, Property
from app.utils.auth import get_current_landlord
from app.utils import appwrite_service as aws

router = APIRouter(prefix="/media", tags=["Media"])

# What we'll accept.  Note: we also accept octet-stream and remap it to jpeg
# so that camera images that arrive without a proper MIME type still work.
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/heic", "image/heif",
    "application/octet-stream",   # ← camera fallback — remapped in appwrite_service
}
ALLOWED_DOC_TYPES = {
    "image/jpeg", "image/png",
    "image/heic", "image/heif",
    "application/pdf",
    "application/octet-stream",   # ← same fallback for ID card photos
}


def _check_file(file: UploadFile, allowed: set):
    ct = (file.content_type or "").strip().lower()
    if ct not in allowed:
        raise HTTPException(
            400,
            f"File type '{ct}' not allowed. "
            f"Accepted: {', '.join(sorted(allowed - {'application/octet-stream'}))}",
        )


# ── Debug ─────────────────────────────────────────────────────────────────────

@router.get("/debug/appwrite")
async def debug_appwrite():
    """
    Verify Appwrite env vars and bucket reachability.
    Remove this endpoint (or protect it) before going to production.
    """
    return await aws.debug_config()


# ── Tenant Photo ──────────────────────────────────────────────────────────────

@router.post("/tenant/{tenant_id}/photo")
async def upload_tenant_photo(
    tenant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    _check_file(file, ALLOWED_IMAGE_TYPES)

    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord.landlord_id,
    ).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    result = await aws.upload_tenant_photo(file)
    tenant.photo_url = result["url"]
    db.commit()

    return {"success": True, "photo_url": result["url"], "file_id": result["file_id"]}


# ── Tenant ID Card ─────────────────────────────────────────────────────────────

@router.post("/tenant/{tenant_id}/id-card")
async def upload_tenant_id_card(
    tenant_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    _check_file(file, ALLOWED_DOC_TYPES)

    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord.landlord_id,
    ).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    result = await aws.upload_tenant_id(file)
    tenant.id_card_url = result["url"]
    db.commit()

    return {"success": True, "id_card_url": result["url"], "file_id": result["file_id"]}


# ── Property Image ─────────────────────────────────────────────────────────────

@router.post("/property/{property_id}/image")
async def upload_property_image(
    property_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    _check_file(file, ALLOWED_IMAGE_TYPES)

    prop = db.query(Property).filter(
        Property.property_id == property_id,
        Property.landlord_id == landlord.landlord_id,
    ).first()
    if not prop:
        raise HTTPException(404, "Property not found")

    result = await aws.upload_property_image(file)

    urls: list = list(prop.photo_urls or [])
    urls.append(result["url"])
    prop.photo_urls = urls
    db.commit()

    return {
        "success":      True,
        "image_url":    result["url"],
        "file_id":      result["file_id"],
        "total_images": len(urls),
    }













# # app/api/routers/media.py
# """
# Media upload endpoints – delegates to Appwrite via appwrite_service.
# """
# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models import Tenant, Property
# from app.utils.auth import get_current_landlord
# from app.utils import appwrite_service as aws

# router = APIRouter(prefix="/media", tags=["Media"])

# ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}
# ALLOWED_DOC_TYPES   = {"image/jpeg", "image/png", "application/pdf"}
# MAX_SIZE_MB = 10


# def _check_file(file: UploadFile, allowed: set):
#     if file.content_type not in allowed:
#         raise HTTPException(
#             400,
#             f"File type '{file.content_type}' not allowed. Accepted: {', '.join(allowed)}"
#         )


# # ── Tenant Photo ─────────────────────────────────────────────────────────────

# @router.post("/tenant/{tenant_id}/photo")
# async def upload_tenant_photo(
#     tenant_id: int,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord),
# ):
#     _check_file(file, ALLOWED_IMAGE_TYPES)
#     tenant = db.query(Tenant).filter(
#         Tenant.tenant_id == tenant_id,
#         Tenant.landlord_id == landlord.landlord_id
#     ).first()
#     if not tenant:
#         raise HTTPException(404, "Tenant not found")

#     result = await aws.upload_tenant_photo(file)
#     tenant.photo_url = result["url"]
#     db.commit()

#     return {"success": True, "photo_url": result["url"], "file_id": result["file_id"]}


# # ── Tenant ID Card ────────────────────────────────────────────────────────────

# @router.post("/tenant/{tenant_id}/id-card")
# async def upload_tenant_id_card(
#     tenant_id: int,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord),
# ):
#     _check_file(file, ALLOWED_DOC_TYPES)
#     tenant = db.query(Tenant).filter(
#         Tenant.tenant_id == tenant_id,
#         Tenant.landlord_id == landlord.landlord_id
#     ).first()
#     if not tenant:
#         raise HTTPException(404, "Tenant not found")

#     result = await aws.upload_tenant_id(file)
#     tenant.id_card_url = result["url"]
#     db.commit()

#     return {"success": True, "id_card_url": result["url"], "file_id": result["file_id"]}


# # ── Property Image ────────────────────────────────────────────────────────────

# @router.post("/property/{property_id}/image")
# async def upload_property_image(
#     property_id: int,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord),
# ):
#     _check_file(file, ALLOWED_IMAGE_TYPES)
#     prop = db.query(Property).filter(
#         Property.property_id == property_id,
#         Property.landlord_id == landlord.landlord_id
#     ).first()
#     if not prop:
#         raise HTTPException(404, "Property not found")

#     result = await aws.upload_property_image(file)

#     # Append to photo_urls list
#     urls: list = prop.photo_urls or []
#     urls.append(result["url"])
#     prop.photo_urls = urls
#     db.commit()

#     return {
#         "success": True,
#         "image_url": result["url"],
#         "file_id": result["file_id"],
#         "total_images": len(urls),
#     }

# # Add to app/api/routers/media.py temporarily

# @router.get("/debug/appwrite")
# async def debug_appwrite():
#     import os
#     endpoint   = os.getenv("APPWRITE_ENDPOINT", "").strip()
#     project_id = os.getenv("APPWRITE_PROJECT_ID", "").strip()
#     api_key    = os.getenv("APPWRITE_API_KEY", "").strip()
#     bucket_id  = os.getenv("APPWRITE_BUCKET_ID", "").strip()

#     # Test actual connection
#     import httpx
#     headers = {
#         "X-Appwrite-Project": project_id,
#         "X-Appwrite-Key":     api_key,
#     }
#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             r = await client.get(
#                 f"{endpoint}/storage/buckets/{bucket_id}",
#                 headers=headers,
#             )
#         bucket_response = r.json()
#         bucket_status   = r.status_code
#     except Exception as e:
#         bucket_response = str(e)
#         bucket_status   = -1

#     return {
#         "endpoint":       endpoint,
#         "project_id":     project_id,
#         "api_key_set":    bool(api_key),
#         "api_key_prefix": api_key[:8] + "..." if len(api_key) > 8 else "TOO SHORT",
#         "bucket_id":      bucket_id,
#         "bucket_status":  bucket_status,
#         "bucket_response": bucket_response,
#     }