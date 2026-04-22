"""
Agreements router
Endpoints:
  GET  /agreements/{tenant_id}/generate  → preview PDF (not signed yet)
  POST /agreements/{tenant_id}/sign      → mark signed + upload to Appwrite
  GET  /agreements/{tenant_id}/download  → download signed PDF
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ...database import get_db
from ...models import Tenant, Room, Property, Landlord
from ...utils.auth import get_current_landlord
from ...utils.agreement_generator import generate_tenancy_agreement
from ...utils import appwrite_service as aws

router = APIRouter(prefix="/agreements", tags=["Agreements"])


def _get_tenant_or_404(tenant_id: int, landlord_id: int, db: Session) -> Tenant:
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord_id,
    ).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


def _build_agreement_data(tenant: Tenant, db: Session) -> dict:
    """Assembles the dict required by generate_tenancy_agreement()."""
    room = None
    property_obj = None
    landlord = None

    if tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
        if room:
            property_obj = db.query(Property).filter(
                Property.property_id == room.property_id
            ).first()
            if property_obj:
                landlord = db.query(Landlord).filter(
                    Landlord.landlord_id == property_obj.landlord_id
                ).first()

    prop_type = "hostel"
    if property_obj and property_obj.property_type:
        prop_type = (
            property_obj.property_type.value
            if hasattr(property_obj.property_type, "value")
            else str(property_obj.property_type)
        )

    unit_label = "Room" if prop_type == "hostel" else "Unit"

    return {
        "landlord_name":    landlord.name if landlord else "Landlord",
        "landlord_phone":   landlord.phone_number if landlord else "",
        "landlord_email":   landlord.email if landlord else "",
        "tenant_name":      tenant.full_name,
        "tenant_phone":     tenant.phone_number,
        "tenant_email":     tenant.email or "",
        "tenant_id_number": tenant.id_card_number or "",
        "property_name":    property_obj.name if property_obj else "Property",
        "property_address": property_obj.location if property_obj else "",
        "property_type":    prop_type,
        "unit_label":       unit_label,
        "unit_number":      room.room_number if room else "N/A",
        "rent_amount":      room.rent_amount if room else 0.0,
        "payment_due_day":  room.due_date if room else 1,
        "lease_start":      datetime.utcnow().date(),
        "lease_end":        None,
        "deposit_amount":   (room.rent_amount if room else 0.0),
        "receipt_number":   f"AGR-{tenant.tenant_id:05d}",
        "generated_at":     datetime.utcnow(),
    }


@router.get("/{tenant_id}/generate")
def generate_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    """Generate (preview) a tenancy agreement PDF. Does not mark as signed."""
    tenant = _get_tenant_or_404(tenant_id, landlord.landlord_id, db)
    data = _build_agreement_data(tenant, db)
    pdf_buffer = generate_tenancy_agreement(data)

    filename = f"agreement_preview_{tenant_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/{tenant_id}/sign")
async def sign_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    """
    Mark the tenant agreement as signed.
    Generates the final PDF and uploads it to Appwrite for permanent storage.
    """
    tenant = _get_tenant_or_404(tenant_id, landlord.landlord_id, db)

    if tenant.agreement_signed:
        return {
            "success": True,
            "message": "Already signed",
            "agreement_url": tenant.agreement_url,
        }

    data = _build_agreement_data(tenant, db)
    pdf_buffer = generate_tenancy_agreement(data)
    pdf_bytes = pdf_buffer.read()

    filename = f"agreement_tenant_{tenant_id}_{int(datetime.utcnow().timestamp())}.pdf"

    try:
        result = await aws.upload_agreement_pdf(pdf_bytes, filename)
        tenant.agreement_url = result["url"]
        tenant.agreement_file_id = result["file_id"]
    except Exception:
        # Upload failed — still mark as signed locally, URL will be null
        tenant.agreement_url = None
        tenant.agreement_file_id = None

    tenant.agreement_signed = True
    tenant.agreement_signed_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": "Agreement signed and stored",
        "agreement_url": tenant.agreement_url,
        "signed_at": tenant.agreement_signed_at.isoformat(),
    }


@router.get("/{tenant_id}/download")
async def download_agreement(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord=Depends(get_current_landlord),
):
    """
    Download the tenant's signed agreement PDF.
    If Appwrite URL exists, redirects there. Otherwise regenerates on the fly.
    """
    tenant = _get_tenant_or_404(tenant_id, landlord.landlord_id, db)

    # If stored in Appwrite, client can fetch directly — just return the URL
    if tenant.agreement_url:
        return {"agreement_url": tenant.agreement_url}

    # Fallback: regenerate and stream
    data = _build_agreement_data(tenant, db)
    pdf_buffer = generate_tenancy_agreement(data)

    filename = f"agreement_tenant_{tenant_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )











