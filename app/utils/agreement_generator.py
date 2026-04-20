# app/utils/agreement_generator.py
"""
Generates a legally-framed Tenancy Agreement PDF for Cameroonian landlords.
Uses ReportLab. Designed to be evidence-grade for dispute resolution.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime, date
from typing import Optional


# ── Brand colors ──────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0A1F44")
GREEN  = colors.HexColor("#1FBF75")
GRAY   = colors.HexColor("#6B7280")
LIGHT  = colors.HexColor("#F5F7FA")
BLACK  = colors.HexColor("#1E1E1E")
ORANGE = colors.HexColor("#FF8A00")


def _styles():
    base = getSampleStyleSheet()

    return {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=22, textColor=NAVY,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=11, textColor=GRAY,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4
        ),
        "section_heading": ParagraphStyle(
            "section_heading", fontSize=11, textColor=NAVY,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4
        ),
        "clause_number": ParagraphStyle(
            "clause_number", fontSize=10, textColor=NAVY,
            fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=2
        ),
        "body": ParagraphStyle(
            "body", fontSize=9.5, textColor=BLACK,
            fontName="Helvetica", leading=14, alignment=TA_JUSTIFY,
            spaceAfter=4
        ),
        "small": ParagraphStyle(
            "small", fontSize=8.5, textColor=GRAY,
            fontName="Helvetica", leading=12
        ),
        "label": ParagraphStyle(
            "label", fontSize=9, textColor=GRAY,
            fontName="Helvetica-Bold", spaceAfter=2
        ),
        "value": ParagraphStyle(
            "value", fontSize=10, textColor=BLACK,
            fontName="Helvetica", spaceAfter=6
        ),
        "warning": ParagraphStyle(
            "warning", fontSize=9.5, textColor=ORANGE,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
            spaceBefore=8, spaceAfter=8
        ),
        "signature_label": ParagraphStyle(
            "signature_label", fontSize=9, textColor=GRAY,
            fontName="Helvetica", alignment=TA_CENTER
        ),
    }


def _info_table(rows: list[tuple[str, str]], s) -> Table:
    data = [[Paragraph(k, s["label"]), Paragraph(v or "—", s["value"])] for k, v in rows]
    t = Table(data, colWidths=[3.5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E9F0")),
    ]))
    return t


def generate_tenancy_agreement(data: dict) -> BytesIO:
    """
    Generate a fully drafted tenancy agreement PDF.

    Required keys in `data`:
        landlord_name, landlord_phone, landlord_email (optional)
        tenant_name, tenant_phone, tenant_email (optional)
        tenant_id_number (national ID / matric)
        property_name, property_address, property_type  ('hostel'|'residential')
        unit_label  ('Room'|'Apartment'|'Unit')
        unit_number
        rent_amount (float, FCFA)
        payment_due_day  (int, day of month)
        lease_start  (date)
        lease_end    (date | None → open-ended)
        deposit_amount (float, FCFA)
        receipt_number  (str)
        generated_at    (datetime | None → now)
    """

    buf = BytesIO()
    s = _styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=2 * cm,
        title=f"Propti Tenancy Agreement – {data.get('tenant_name', '')}",
    )

    unit_label    = data.get("unit_label", "Room")
    prop_type     = data.get("property_type", "hostel")
    rent          = int(data.get("rent_amount", 0))
    due_day       = data.get("payment_due_day", 1)
    deposit       = int(data.get("deposit_amount", 0))
    lease_start   = data.get("lease_start")
    lease_end     = data.get("lease_end")
    generated_at  = data.get("generated_at") or datetime.now()

    lease_start_str = lease_start.strftime("%d %B %Y") if isinstance(lease_start, (date, datetime)) else str(lease_start or "—")
    lease_end_str   = lease_end.strftime("%d %B %Y") if isinstance(lease_end, (date, datetime)) else (str(lease_end) if lease_end else "Month-to-month (no fixed end date)")

    elements = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("<b><font color='#0A1F44' size='18'>P</font><font color='#1FBF75' size='18'>.</font></b>", ParagraphStyle("logo", fontSize=20, fontName="Helvetica-Bold")),
        Paragraph("<b>PROPTI</b><br/><font size='8' color='#6B7280'>Accountability Platform</font>",
                  ParagraphStyle("brand", fontSize=13, fontName="Helvetica-Bold", textColor=NAVY)),
        Paragraph(f"Generated: {generated_at.strftime('%d/%m/%Y %H:%M') if isinstance(generated_at, datetime) else generated_at}<br/>"
                  f"Ref: {data.get('receipt_number', 'N/A')}",
                  ParagraphStyle("ref", fontSize=8, textColor=GRAY, alignment=2)),
    ]]
    header_t = Table(header_data, colWidths=[1.5 * cm, 10 * cm, 5.5 * cm])
    header_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(header_t)
    elements.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    elements.append(Spacer(1, 0.3 * cm))

    # ── TITLE ─────────────────────────────────────────────────────────────────
    elements.append(Paragraph("RESIDENTIAL TENANCY AGREEMENT", s["cover_title"]))
    elements.append(Paragraph(
        f"{data.get('property_name', '')} · {unit_label} {data.get('unit_number', '')}",
        s["cover_sub"]
    ))
    elements.append(Spacer(1, 0.4 * cm))

    # ── PARTIES ───────────────────────────────────────────────────────────────
    elements.append(Paragraph("A. PARTIES TO THIS AGREEMENT", s["section_heading"]))
    elements.append(_info_table([
        ("LANDLORD",        data.get("landlord_name", "")),
        ("Phone",           data.get("landlord_phone", "")),
        ("Email",           data.get("landlord_email", "") or "—"),
    ], s))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(_info_table([
        ("TENANT",          data.get("tenant_name", "")),
        ("Phone",           data.get("tenant_phone", "")),
        ("Email",           data.get("tenant_email", "") or "—"),
        ("National ID / Matric", data.get("tenant_id_number", "")),
    ], s))

    # ── PREMISES ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("B. PREMISES", s["section_heading"]))
    elements.append(_info_table([
        ("Property",        data.get("property_name", "")),
        ("Address",         data.get("property_address", "")),
        ("Type",            "Student Hostel" if prop_type == "hostel" else "Residential"),
        (unit_label,        str(data.get("unit_number", ""))),
    ], s))

    # ── FINANCIAL TERMS ───────────────────────────────────────────────────────
    elements.append(Paragraph("C. FINANCIAL TERMS", s["section_heading"]))
    elements.append(_info_table([
        ("Monthly Rent",    f"{rent:,} FCFA"),
        ("Security Deposit",f"{deposit:,} FCFA (non-refundable if lease violated)"),
        ("Payment Due",     f"On or before the {due_day}{_ordinal(due_day)} day of each month"),
        ("Lease Start",     lease_start_str),
        ("Lease End",       lease_end_str),
        ("Accepted Methods","Cash · Mobile Money (MTN/Orange) · Bank Transfer"),
    ], s))

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E9F0")))

    # ── TERMS AND CONDITIONS ──────────────────────────────────────────────────
    elements.append(Paragraph("D. TERMS AND CONDITIONS", s["section_heading"]))

    clauses = _build_clauses(rent, due_day, deposit, unit_label, prop_type)
    for title, text in clauses:
        elements.append(KeepTogether([
            Paragraph(title, s["clause_number"]),
            Paragraph(text,  s["body"]),
        ]))

    # ── SPECIAL CONDITIONS ────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("E. SPECIAL CONDITIONS", s["section_heading"]))
    elements.append(Paragraph(
        "Any additional conditions agreed between the parties must be written below and initialled "
        "by both parties to be enforceable:",
        s["body"]
    ))
    for _ in range(4):
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=12))

    # ── ACKNOWLEDGEMENT ───────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("F. ACKNOWLEDGEMENT & SIGNATURES", s["section_heading"]))
    elements.append(Paragraph(
        "Both parties declare that they have read, understood, and voluntarily agree to all terms "
        "set out in this agreement. This document is legally binding under the laws of the Republic "
        "of Cameroon and may be submitted as evidence in any competent court or tribunal.",
        s["body"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # Signature blocks
    sig_data = [[
        _sig_block("LANDLORD SIGNATURE", data.get("landlord_name", ""), s),
        _sig_block("TENANT SIGNATURE", data.get("tenant_name", ""),    s),
    ]]
    sig_table = Table(sig_data, colWidths=[8.5 * cm, 8.5 * cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN",  (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)

    # Digital signature placeholder
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(
        "✦  DIGITAL SIGNATURE CAPTURED VIA PROPTI PLATFORM  ✦",
        s["warning"]
    ))
    elements.append(Paragraph(
        f"Agreement reference: {data.get('receipt_number', 'N/A')} · "
        f"Stored securely on Propti · {generated_at.strftime('%d %B %Y %H:%M') if isinstance(generated_at, datetime) else ''}",
        s["small"]
    ))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E9F0")))
    elements.append(Spacer(1, 0.15 * cm))
    elements.append(Paragraph(
        "This agreement was generated by <b>Propti</b> — the accountability platform for landlords in Cameroon. "
        "www.propti.app · support@propti.app",
        ParagraphStyle("footer", fontSize=7.5, textColor=GRAY, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buf.seek(0)
    return buf


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _sig_block(title: str, name: str, s) -> list:
    return [
        Paragraph(f"<b>{title}</b>", s["signature_label"]),
        Spacer(1, 0.6 * cm),
        HRFlowable(width="90%", thickness=1, color=NAVY),
        Paragraph(f"Name: {name}", s["signature_label"]),
        Spacer(1, 0.4 * cm),
        HRFlowable(width="90%", thickness=0.5, color=colors.lightgrey),
        Paragraph("Date: ___________________", s["signature_label"]),
    ]


def _build_clauses(rent: int, due_day: int, deposit: int, unit_label: str, prop_type: str) -> list:
    """Returns list of (clause_title, clause_text) tuples."""

    hostel_extras = ""
    if prop_type == "hostel":
        hostel_extras = (
            " The Tenant acknowledges that this accommodation is provided primarily for "
            "students and academic purposes. Excessive noise, disruption of other residents' "
            "studies, or behaviour incompatible with an academic environment is grounds for "
            "immediate termination."
        )

    return [
        ("1. RENT PAYMENT OBLIGATION",
         f"The Tenant agrees to pay the sum of <b>{rent:,} FCFA</b> monthly as rent for the "
         f"occupied {unit_label}. Payment is due on or before the <b>{due_day}{_ordinal(due_day)} day of each "
         f"calendar month</b> without exception, demand, or reminder. Failure to pay by the due date "
         f"constitutes a breach of this agreement."),

        ("2. LATE PAYMENT PENALTY",
         f"If rent is not received in full by the {due_day}{_ordinal(due_day)} of the month, a late fee of "
         f"<b>5% of the monthly rent ({int(rent * 0.05):,} FCFA)</b> shall be added to the outstanding "
         f"balance for every 7-day period the payment remains outstanding. Continued non-payment "
         f"beyond 30 days will result in formal notice to vacate."),

        ("3. SECURITY DEPOSIT",
         f"A security deposit of <b>{deposit:,} FCFA</b> is payable upon signing this agreement. "
         f"This deposit will be refunded within 30 days of the Tenant vacating the premises, "
         f"subject to deductions for: unpaid rent, damage beyond normal wear and tear, cleaning "
         f"costs, or any costs arising from breach of this agreement. The deposit does not serve "
         f"as payment for the last month's rent."),

        ("4. DAMAGE TO PROPERTY",
         f"The Tenant is fully responsible for any damage caused to the {unit_label}, fixtures, "
         f"fittings, furniture, or communal areas by the Tenant, their guests, or invitees. "
         f"Damage includes but is not limited to: broken windows, damaged doors/locks, damaged "
         f"plumbing or electrical fittings, stained or damaged walls, and broken furniture. "
         f"The cost of repair or replacement will be charged to the Tenant and must be paid "
         f"within 14 days of written notification. Failure to pay constitutes grounds for "
         f"legal action and may be presented as evidence before a competent court."),

        ("5. PROHIBITED ACTIVITIES",
         f"The Tenant shall NOT: sublease or allow other persons to occupy the {unit_label} without "
         f"prior written consent from the Landlord; conduct any commercial, illegal, or immoral "
         f"activities on the premises; keep animals or pets without written permission; "
         f"make structural alterations to the property; store flammable, explosive, or hazardous "
         f"materials; or disturb the peace of other residents between the hours of 10:00 PM and "
         f"6:00 AM.{hostel_extras}"),

        ("6. MAINTENANCE AND CLEANLINESS",
         f"The Tenant shall maintain the {unit_label} in a clean and sanitary condition at all "
         f"times. The Tenant is responsible for minor maintenance such as replacing light bulbs, "
         f"keeping drains clear, and ensuring rubbish is properly disposed of. Any maintenance "
         f"issues that are the Landlord's responsibility must be reported in writing within "
         f"48 hours of discovery; failure to report damage in a timely manner may make the "
         f"Tenant liable for resulting deterioration."),

        ("7. UTILITY USAGE",
         "The Tenant agrees to use water and electricity responsibly and not to waste shared "
         "resources. Any damage to utility infrastructure caused by misuse (e.g., blocked pipes "
         "from improper waste disposal, circuit damage from overloading) will be charged to the "
         "Tenant. The Tenant shall comply with any utility usage rules posted or communicated "
         "by the Landlord."),

        ("8. ENTRY BY LANDLORD",
         "The Landlord or their authorised representative has the right to enter the premises "
         "for inspection, repair, or showing to prospective tenants, with a minimum of "
         "<b>24 hours' notice</b> except in emergencies. The Tenant shall not unreasonably "
         "refuse access."),

        ("9. TERMINATION OF AGREEMENT",
         "Either party may terminate this agreement by giving <b>30 days' written notice</b>. "
         "The Landlord may terminate this agreement without notice in cases of: non-payment of "
         "rent exceeding 30 days; serious breach of any clause of this agreement; criminal "
         "activity on the premises; or conduct causing harm to other residents or the property. "
         "Upon termination, the Tenant must vacate the premises, return all keys, and leave the "
         f"{unit_label} in a clean and undamaged condition."),

        ("10. EVIDENCE AND LEGAL PROCEEDINGS",
         "Both parties acknowledge that this agreement, along with payment records maintained "
         "on the Propti platform, photographs, and any written communications, shall constitute "
         "admissible evidence in any legal proceedings before a Cameroonian court or tribunal. "
         "By signing this agreement, the Tenant consents to Propti storing and processing their "
         "personal data, agreement, and payment records in accordance with applicable data "
         "protection laws."),

        ("11. GOVERNING LAW",
         "This agreement is governed by and construed in accordance with the laws of the "
         "Republic of Cameroon. Any dispute arising from this agreement shall first be resolved "
         "amicably. If amicable resolution fails, the matter shall be referred to the competent "
         "court of jurisdiction in the locality where the property is situated."),
    ]