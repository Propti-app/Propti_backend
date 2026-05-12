# app/utils/appwrite_service.py
"""
Appwrite storage service for Propti.
Single-bucket setup (free plan). All media goes to APPWRITE_BUCKET_ID.
"""
import os
import uuid
import httpx
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv

load_dotenv()

APPWRITE_ENDPOINT   = os.getenv("APPWRITE_ENDPOINT", "https://fra.cloud.appwrite.io/v1").strip().rstrip("/")
APPWRITE_PROJECT_ID = (os.getenv("APPWRITE_PROJECT_ID") or "").strip()
APPWRITE_API_KEY    = (os.getenv("APPWRITE_API_KEY") or "").strip()

# ── SINGLE BUCKET (free plan only allows one) ────────────────────────────────
# Must match EXACTLY what you created in the Appwrite console.
# Default matches the Flutter client's AppwriteService.bucketId = 'certificates'
BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID", "certificates").strip()

# All typed helpers point at the same bucket
BUCKET_TENANT_PHOTOS   = BUCKET_ID
BUCKET_TENANT_IDS      = BUCKET_ID
BUCKET_PROPERTY_IMAGES = BUCKET_ID
BUCKET_AGREEMENTS      = BUCKET_ID


def _headers() -> dict:
    return {
        "X-Appwrite-Project": APPWRITE_PROJECT_ID,
        "X-Appwrite-Key":     APPWRITE_API_KEY,
    }


def _check_config():
    if not APPWRITE_PROJECT_ID:
        raise HTTPException(500, "APPWRITE_PROJECT_ID not set in environment")
    if not APPWRITE_API_KEY:
        raise HTTPException(500, "APPWRITE_API_KEY not set in environment")
    if not APPWRITE_ENDPOINT.startswith("http"):
        raise HTTPException(500, f"Invalid APPWRITE_ENDPOINT: '{APPWRITE_ENDPOINT}'")


def _safe_mime(content_type: str | None) -> str:
    """
    Never let 'application/octet-stream' reach Appwrite when we know
    the file is an image.  Fall back to image/jpeg which Appwrite accepts.
    """
    safe = (content_type or "").strip().lower()
    if safe in {"image/jpeg", "image/png", "image/webp", "image/heic",
                "image/heif", "application/pdf"}:
        return safe
    # Unknown / octet-stream → safest fallback for camera images
    return "image/jpeg"


async def upload_file(
    bucket_id: str,
    file: UploadFile,
    file_id: str | None = None,
    prefix: str = "file",
) -> dict:
    """
    Upload any UploadFile to an Appwrite bucket.
    Returns dict with keys: file_id, bucket_id, url, name, size, mime_type.
    """
    _check_config()

    fid      = file_id or str(uuid.uuid4()).replace("-", "")
    content  = await file.read()
    mime     = _safe_mime(file.content_type)

    # Use a meaningful filename stored in Appwrite
    ext_map  = {"image/jpeg": "jpg", "image/png": "png",
                 "image/webp": "webp", "image/heic": "heic",
                 "application/pdf": "pdf"}
    ext      = ext_map.get(mime, "jpg")
    filename = f"{prefix}_{fid}.{ext}"

    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers=_headers(),
            files={"file": (filename, content, mime)},
            data={"fileId": fid},
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(
            502,
            f"Appwrite upload failed [{resp.status_code}]: {resp.text}",
        )

    data     = resp.json()
    view_url = (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}"
        f"/files/{fid}/view?project={APPWRITE_PROJECT_ID}"
    )

    return {
        "file_id":   data["$id"],
        "bucket_id": bucket_id,
        "name":      data.get("name"),
        "size":      data.get("sizeOriginal"),
        "mime_type": data.get("mimeType"),
        "url":       view_url,
    }


async def delete_file(bucket_id: str, file_id: str) -> bool:
    _check_config()
    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.delete(url, headers=_headers())
    return resp.status_code == 204


def get_file_view_url(bucket_id: str, file_id: str) -> str:
    return (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}"
        f"/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
    )


# ── Typed helpers ─────────────────────────────────────────────────────────────

async def upload_tenant_photo(file: UploadFile) -> dict:
    return await upload_file(BUCKET_ID, file, prefix="tenant_photo")


async def upload_tenant_id(file: UploadFile) -> dict:
    return await upload_file(BUCKET_ID, file, prefix="tenant_id")


async def upload_property_image(file: UploadFile) -> dict:
    return await upload_file(BUCKET_ID, file, prefix="property_img")


async def upload_agreement_pdf(pdf_bytes: bytes, filename: str) -> dict:
    """Upload a pre-generated PDF (bytes, not UploadFile)."""
    _check_config()

    fid = str(uuid.uuid4()).replace("-", "")
    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_ID}/files"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            url,
            headers=_headers(),
            files={"file": (filename, pdf_bytes, "application/pdf")},
            data={"fileId": fid},
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(
            502,
            f"Appwrite agreement upload failed [{resp.status_code}]: {resp.text}",
        )

    data     = resp.json()
    view_url = (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_ID}"
        f"/files/{fid}/view?project={APPWRITE_PROJECT_ID}"
    )
    return {"file_id": data["$id"], "bucket_id": BUCKET_ID, "url": view_url}


# ── Debug helper (mount this route temporarily to verify config) ──────────────

async def debug_config() -> dict:
    """Call GET /media/debug/appwrite to verify env vars and bucket access."""
    _check_config()
    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_ID}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=_headers())
        bucket_ok   = resp.status_code == 200
        bucket_data = resp.json()
    except Exception as e:
        bucket_ok   = False
        bucket_data = str(e)

    return {
        "endpoint":        APPWRITE_ENDPOINT,
        "project_id":      APPWRITE_PROJECT_ID,
        "api_key_set":     bool(APPWRITE_API_KEY),
        "api_key_prefix":  APPWRITE_API_KEY[:8] + "..." if len(APPWRITE_API_KEY) > 8 else "TOO SHORT",
        "bucket_id":       BUCKET_ID,
        "bucket_reachable": bucket_ok,
        "bucket_data":     bucket_data,
    }



# standard_d859b75f33bfbc550088b1f00a313a0850a3ee9bffe12e9d9b3e816bca2a0119cf54f487b69b7583d61593cb0f220bfb05d5aca745daf528d5ef187fbe673ade3513bdfa11d0980f71dfb49b9d39e828e6edcfacab3ce5695bcf404469b5b8d77bb63a9e7f3c6c475a593310764f530088f6d4fa064b81a1f3efc78edb3f7e3c








# # app/utils/appwrite_service.py
# import os
# import httpx
# import uuid
# from fastapi import UploadFile, HTTPException
# from dotenv import load_dotenv

# load_dotenv()

# APPWRITE_ENDPOINT   = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1").strip()
# APPWRITE_PROJECT_ID = (os.getenv("APPWRITE_PROJECT_ID") or "").strip()
# APPWRITE_API_KEY    = (os.getenv("APPWRITE_API_KEY") or "").strip()

# # ONE bucket for everything — free plan
# BUCKET_ID = os.getenv("APPWRITE_BUCKET_ID", "certificates").strip()

# # Keep these pointing to the same single bucket
# BUCKET_TENANT_PHOTOS   = BUCKET_ID
# BUCKET_TENANT_IDS      = BUCKET_ID
# BUCKET_PROPERTY_IMAGES = BUCKET_ID
# BUCKET_AGREEMENTS      = BUCKET_ID


# def _headers() -> dict:
#     return {
#         "X-Appwrite-Project": APPWRITE_PROJECT_ID,
#         "X-Appwrite-Key": APPWRITE_API_KEY,
#     }


# def _check_config():
#     if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
#         raise HTTPException(status_code=500, detail="Appwrite credentials not configured")
#     if not APPWRITE_ENDPOINT.startswith("http"):
#         raise HTTPException(status_code=500, detail=f"Invalid Appwrite endpoint: '{APPWRITE_ENDPOINT}'")


# async def upload_file(
#     bucket_id: str,
#     file: UploadFile,
#     file_id: str | None = None,
#     prefix: str = "file",
# ) -> dict:
#     _check_config()

#     file_id  = file_id or str(uuid.uuid4()).replace("-", "")
#     content  = await file.read()
#     filename = f"{prefix}_{file_id}"  # readable name stored in Appwrite

#     url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files"

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(
#             url,
#             headers=_headers(),
#             files={"file": (filename, content, file.content_type or "application/octet-stream")},
#             data={"fileId": file_id},
#         )

#     if response.status_code not in (200, 201):
#         raise HTTPException(
#             status_code=502,
#             detail=f"Appwrite upload failed [{response.status_code}]: {response.text}",
#         )

#     data     = response.json()
#     view_url = (
#         f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}"
#         f"/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
#     )

#     return {
#         "file_id":   data["$id"],
#         "bucket_id": bucket_id,
#         "name":      data.get("name"),
#         "size":      data.get("sizeOriginal"),
#         "mime_type": data.get("mimeType"),
#         "url":       view_url,
#     }


# async def delete_file(bucket_id: str, file_id: str) -> bool:
#     _check_config()
#     url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}"
#     async with httpx.AsyncClient(timeout=15) as client:
#         response = await client.delete(url, headers=_headers())
#     return response.status_code == 204


# def get_file_view_url(bucket_id: str, file_id: str) -> str:
#     return (
#         f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}"
#         f"/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
#     )


# # ── Typed helpers (all use the same single bucket) ───────────────────────────

# async def upload_tenant_photo(file: UploadFile) -> dict:
#     return await upload_file(BUCKET_ID, file, prefix="tenant_photo")

# async def upload_tenant_id(file: UploadFile) -> dict:
#     return await upload_file(BUCKET_ID, file, prefix="tenant_id")

# async def upload_property_image(file: UploadFile) -> dict:
#     return await upload_file(BUCKET_ID, file, prefix="property_img")

# async def upload_agreement_pdf(pdf_bytes: bytes, filename: str) -> dict:
#     _check_config()
#     file_id = str(uuid.uuid4()).replace("-", "")
#     url     = f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_ID}/files"

#     async with httpx.AsyncClient(timeout=30) as client:
#         response = await client.post(
#             url,
#             headers=_headers(),
#             files={"file": (filename, pdf_bytes, "application/pdf")},
#             data={"fileId": file_id},
#         )

#     if response.status_code not in (200, 201):
#         raise HTTPException(
#             status_code=502,
#             detail=f"Appwrite agreement upload failed: {response.text}",
#         )

#     data     = response.json()
#     view_url = (
#         f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_ID}"
#         f"/files/{file_id}/view?project={APPWRITE_PROJECT_ID}"
#     )
#     return {"file_id": data["$id"], "bucket_id": BUCKET_ID, "url": view_url}











# # # app/utils/appwrite_service.py
# # """
# # Appwrite storage service for Propti
# # Handles: tenant photos, ID cards, property images, signed agreements
# # """

# # import os
# # import httpx
# # from fastapi import UploadFile, HTTPException
# # from dotenv import load_dotenv
# # import uuid

# # load_dotenv()

# # APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
# # APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
# # APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

# # # Bucket IDs – create these in your Appwrite console
# # BUCKET_TENANT_PHOTOS   = os.getenv("APPWRITE_BUCKET_TENANT_PHOTOS", "tenant_photos")
# # BUCKET_TENANT_IDS      = os.getenv("APPWRITE_BUCKET_TENANT_IDS", "tenant_ids")
# # BUCKET_PROPERTY_IMAGES = os.getenv("APPWRITE_BUCKET_PROPERTY_IMAGES", "property_images")
# # BUCKET_AGREEMENTS      = os.getenv("APPWRITE_BUCKET_AGREEMENTS", "agreements")


# # def _headers() -> dict:
# #     return {
# #         "X-Appwrite-Project": APPWRITE_PROJECT_ID,
# #         "X-Appwrite-Key": APPWRITE_API_KEY,
# #     }


# # async def upload_file(bucket_id: str, file: UploadFile, file_id: str | None = None) -> dict:
# #     """
# #     Upload a file to an Appwrite bucket.
# #     Returns the file metadata including file_id and view URL.
# #     """
# #     if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
# #         raise HTTPException(status_code=500, detail="Appwrite not configured")

# #     file_id = file_id or str(uuid.uuid4()).replace("-", "")[:36]
# #     content = await file.read()

# #     url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files"

# #     async with httpx.AsyncClient() as client:
# #         response = await client.post(
# #             url,
# #             headers=_headers(),
# #             files={"file": (file.filename, content, file.content_type)},
# #             data={"fileId": file_id},
# #         )

# #     if response.status_code not in (200, 201):
# #         raise HTTPException(
# #             status_code=502,
# #             detail=f"Appwrite upload failed: {response.text}",
# #         )

# #     data = response.json()
# #     view_url = (
# #         f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}/view"
# #         f"?project={APPWRITE_PROJECT_ID}"
# #     )

# #     return {
# #         "file_id": data["$id"],
# #         "bucket_id": bucket_id,
# #         "name": data.get("name"),
# #         "size": data.get("sizeOriginal"),
# #         "mime_type": data.get("mimeType"),
# #         "url": view_url,
# #     }


# # async def delete_file(bucket_id: str, file_id: str) -> bool:
# #     """Delete a file from Appwrite."""
# #     url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}"
# #     async with httpx.AsyncClient() as client:
# #         response = await client.delete(url, headers=_headers())
# #     return response.status_code == 204


# # def get_file_view_url(bucket_id: str, file_id: str) -> str:
# #     """Build a direct view URL for a stored file."""
# #     return (
# #         f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}/view"
# #         f"?project={APPWRITE_PROJECT_ID}"
# #     )


# # async def upload_tenant_photo(file: UploadFile) -> dict:
# #     return await upload_file(BUCKET_TENANT_PHOTOS, file)


# # async def upload_tenant_id(file: UploadFile) -> dict:
# #     return await upload_file(BUCKET_TENANT_IDS, file)


# # async def upload_property_image(file: UploadFile) -> dict:
# #     return await upload_file(BUCKET_PROPERTY_IMAGES, file)


# # async def upload_agreement_pdf(pdf_bytes: bytes, filename: str) -> dict:
# #     """Upload a signed agreement PDF (bytes, not UploadFile)."""
# #     if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
# #         raise HTTPException(status_code=500, detail="Appwrite not configured")

# #     file_id = str(uuid.uuid4()).replace("-", "")[:36]
# #     url = f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_AGREEMENTS}/files"

# #     async with httpx.AsyncClient() as client:
# #         response = await client.post(
# #             url,
# #             headers=_headers(),
# #             files={"file": (filename, pdf_bytes, "application/pdf")},
# #             data={"fileId": file_id},
# #         )

# #     if response.status_code not in (200, 201):
# #         raise HTTPException(
# #             status_code=502,
# #             detail=f"Appwrite agreement upload failed: {response.text}",
# #         )

# #     data = response.json()
# #     view_url = (
# #         f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_AGREEMENTS}/files/{file_id}/view"
# #         f"?project={APPWRITE_PROJECT_ID}"
# #     )

# #     return {
# #         "file_id": data["$id"],
# #         "bucket_id": BUCKET_AGREEMENTS,
# #         "url": view_url,
# #     }