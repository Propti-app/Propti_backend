# app/api/routers/agreements.py
"""
Tenancy Agreement endpoints:
  POST /agreements/{tenant_id}/generate  – generate unsigned PDF
  POST /agreements/{tenant_id}/sign      – mark as signed, store in Appwrite
  GET  /agreements/{tenant_id}/download  – stream PDF for landlord
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models import Tenant, Room, Property, Landlord
from app.utils.auth import get_current_landlord
from app.utils.agreement_generator import generate_tenancy_agreement
from app.utils.appwrite_service import upload_agreement_pdf, get_file_view_url, BUCKET_AGREEMENTS
from app.utils.notifications import notify_agreement_signed

router = APIRouter(prefix="/agreements", tags=["Agreements"])


def _build_agreement_data(
    tenant: Tenant,
    room: Room,
    prop: Property,
    landlord: Landlord,
    deposit: float = 0.0,
    lease_end_date=None,
) -> dict:
    prop_type = prop.property_type.value if prop.property_type else "hostel"
    unit_label = "Room" if prop_type == "hostel" else "Unit"

    return {
        "landlord_name":    landlord.name,
        "landlord_phone":   landlord.phone_number,
        "landlord_email":   landlord.email,
        "tenant_name":      tenant.full_name,
        "tenant_phone":     tenant.phone_number,
        "tenant_email":     tenant.email or "",
        "tenant_id_number": tenant.id_card_number or "—",
        "property_name":    prop.name,
        "property_address": prop.location or "—",
        "property_type":    prop_type,
        "unit_label":       unit_label,
        "unit_number":      room.room_number,
        "rent_amount":      room.rent_amount,
        "payment_due_day":  room.due_date,
        "lease_start":      date.today(),
        "lease_end":        lease_end_date,
        "deposit_amount":   deposit or room.rent_amount,  # default = 1 month rent
        "receipt_number":   f"AGR-{tenant.tenant_id:04d}-{datetime.now().strftime('%Y%m%d')}",
        "generated_at":     datetime.now(),
    }


@router.get("/{tenant_id}/generate")
async def generate_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord),
):
    """Stream an unsigned agreement PDF for preview / printing."""
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord.landlord_id
    ).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    if not tenant.assigned_room_id:
        raise HTTPException(400, "Tenant has no assigned room")

    room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
    prop = db.query(Property).filter(Property.property_id == room.property_id).first()

    data = _build_agreement_data(tenant, room, prop, landlord)
    buf  = generate_tenancy_agreement(data)

    filename = f"agreement_{tenant.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


@router.post("/{tenant_id}/sign")
async def sign_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord),
):
    """
    Mark agreement as signed, generate the final PDF, upload to Appwrite,
    store URL on tenant, send landlord push notification.
    """
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord.landlord_id
    ).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    if not tenant.assigned_room_id:
        raise HTTPException(400, "Tenant has no assigned room")

    room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
    prop = db.query(Property).filter(Property.property_id == room.property_id).first()

    # Generate signed PDF
    data = _build_agreement_data(tenant, room, prop, landlord)
    buf  = generate_tenancy_agreement(data)
    pdf_bytes = buf.read()

    filename = f"signed_agreement_{tenant.tenant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # Upload to Appwrite
    try:
        upload_result = await upload_agreement_pdf(pdf_bytes, filename)
        tenant.agreement_url     = upload_result["url"]
        tenant.agreement_file_id = upload_result["file_id"]
    except Exception as e:
        # Store without Appwrite if it fails — don't block signing
        print(f"[Propti] Appwrite upload failed: {e}")
        tenant.agreement_url = None

    tenant.agreement_signed    = True
    tenant.agreement_signed_at = datetime.now()
    db.commit()

    # Push notification to landlord
    if landlord.fcm_token:
        notify_agreement_signed(
            landlord.fcm_token,
            tenant.full_name,
            f"{room.room_number} – {prop.name}",
        )

    return {
        "success": True,
        "tenant_id": tenant_id,
        "tenant_name": tenant.full_name,
        "signed_at": tenant.agreement_signed_at.isoformat(),
        "agreement_url": tenant.agreement_url,
    }


@router.get("/{tenant_id}/download")
async def download_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord),
):
    """
    Re-generate the agreement PDF on demand (for landlord to download).
    If Appwrite URL is available, redirect there; otherwise stream fresh PDF.
    """
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord.landlord_id
    ).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")

    # If stored in Appwrite, redirect
    if tenant.agreement_url:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=tenant.agreement_url)

    # Otherwise generate on-the-fly
    if not tenant.assigned_room_id:
        raise HTTPException(400, "Cannot generate agreement — no room assigned")

    room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
    prop = db.query(Property).filter(Property.property_id == room.property_id).first()

    data = _build_agreement_data(tenant, room, prop, landlord)
    buf  = generate_tenancy_agreement(data)

    filename = f"agreement_{tenant.full_name.replace(' ', '_')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )