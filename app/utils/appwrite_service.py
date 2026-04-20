# app/utils/appwrite_service.py
"""
Appwrite storage service for Propti
Handles: tenant photos, ID cards, property images, signed agreements
"""

import os
import httpx
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv
import uuid

load_dotenv()

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

# Bucket IDs – create these in your Appwrite console
BUCKET_TENANT_PHOTOS   = os.getenv("APPWRITE_BUCKET_TENANT_PHOTOS", "tenant_photos")
BUCKET_TENANT_IDS      = os.getenv("APPWRITE_BUCKET_TENANT_IDS", "tenant_ids")
BUCKET_PROPERTY_IMAGES = os.getenv("APPWRITE_BUCKET_PROPERTY_IMAGES", "property_images")
BUCKET_AGREEMENTS      = os.getenv("APPWRITE_BUCKET_AGREEMENTS", "agreements")


def _headers() -> dict:
    return {
        "X-Appwrite-Project": APPWRITE_PROJECT_ID,
        "X-Appwrite-Key": APPWRITE_API_KEY,
    }


async def upload_file(bucket_id: str, file: UploadFile, file_id: str | None = None) -> dict:
    """
    Upload a file to an Appwrite bucket.
    Returns the file metadata including file_id and view URL.
    """
    if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
        raise HTTPException(status_code=500, detail="Appwrite not configured")

    file_id = file_id or str(uuid.uuid4()).replace("-", "")[:36]
    content = await file.read()

    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=_headers(),
            files={"file": (file.filename, content, file.content_type)},
            data={"fileId": file_id},
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=f"Appwrite upload failed: {response.text}",
        )

    data = response.json()
    view_url = (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}/view"
        f"?project={APPWRITE_PROJECT_ID}"
    )

    return {
        "file_id": data["$id"],
        "bucket_id": bucket_id,
        "name": data.get("name"),
        "size": data.get("sizeOriginal"),
        "mime_type": data.get("mimeType"),
        "url": view_url,
    }


async def delete_file(bucket_id: str, file_id: str) -> bool:
    """Delete a file from Appwrite."""
    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=_headers())
    return response.status_code == 204


def get_file_view_url(bucket_id: str, file_id: str) -> str:
    """Build a direct view URL for a stored file."""
    return (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{bucket_id}/files/{file_id}/view"
        f"?project={APPWRITE_PROJECT_ID}"
    )


async def upload_tenant_photo(file: UploadFile) -> dict:
    return await upload_file(BUCKET_TENANT_PHOTOS, file)


async def upload_tenant_id(file: UploadFile) -> dict:
    return await upload_file(BUCKET_TENANT_IDS, file)


async def upload_property_image(file: UploadFile) -> dict:
    return await upload_file(BUCKET_PROPERTY_IMAGES, file)


async def upload_agreement_pdf(pdf_bytes: bytes, filename: str) -> dict:
    """Upload a signed agreement PDF (bytes, not UploadFile)."""
    if not APPWRITE_PROJECT_ID or not APPWRITE_API_KEY:
        raise HTTPException(status_code=500, detail="Appwrite not configured")

    file_id = str(uuid.uuid4()).replace("-", "")[:36]
    url = f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_AGREEMENTS}/files"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=_headers(),
            files={"file": (filename, pdf_bytes, "application/pdf")},
            data={"fileId": file_id},
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=f"Appwrite agreement upload failed: {response.text}",
        )

    data = response.json()
    view_url = (
        f"{APPWRITE_ENDPOINT}/storage/buckets/{BUCKET_AGREEMENTS}/files/{file_id}/view"
        f"?project={APPWRITE_PROJECT_ID}"
    )

    return {
        "file_id": data["$id"],
        "bucket_id": BUCKET_AGREEMENTS,
        "url": view_url,
    }