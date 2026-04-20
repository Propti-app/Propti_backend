# app/utils/pdf_generator.py - PROFESSIONAL RECEIPT PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_payment_receipt(payment_data: dict) -> BytesIO:
    """
    Generate a professional payment receipt PDF for Cameroonian landlords
    
    Args:
        payment_data: dict with keys:
            - receipt_number
            - tenant_name
            - room_number
            - amount
            - payment_date
            - payment_method
            - period_start
            - period_end
            - remaining_balance
            - landlord_name
            - landlord_contact
    """
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#424242'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_LEFT
    )
    
    # Title
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    elements.append(Paragraph(f"Receipt No: {payment_data['receipt_number']}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Landlord Info
    landlord_info = [
        ["Landlord Information", ""],
        ["Name:", payment_data['landlord_name']],
        ["Contact:", payment_data['landlord_contact']],
    ]
    
    landlord_table = Table(landlord_info, colWidths=[2*inch, 4*inch])
    landlord_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(landlord_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tenant & Payment Info
    payment_info = [
        ["Payment Details", "", "", ""],
        ["Tenant Name:", payment_data['tenant_name'], "Room Number:", payment_data['room_number']],
        ["Payment Date:", payment_data['payment_date'].strftime('%d/%m/%Y') if isinstance(payment_data['payment_date'], datetime) else payment_data['payment_date'], 
         "Payment Method:", payment_data['payment_method']],
        ["Period:", f"{payment_data['period_start']} to {payment_data['period_end']}", "", ""],
    ]
    
    payment_table = Table(payment_info, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (1, 3), (-1, 3)),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Amount Summary
    amount_data = [
        ["Amount Summary", ""],
        ["Amount Paid:", f"{int(payment_data['amount']):,} FCFA"],
        ["Remaining Balance:", f"{int(payment_data['remaining_balance']):,} FCFA"],
        ["Status:", "PAID IN FULL" if payment_data['remaining_balance'] == 0 else "PARTIALLY PAID"],
    ]
    
    amount_table = Table(amount_data, colWidths=[3*inch, 3*inch])
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3e0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#e65100')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 1), (1, 2), 14),
        ('FONTSIZE', (0, 1), (0, -1), 10),
        ('TEXTCOLOR', (1, 1), (1, 2), colors.HexColor('#1976d2')),
        ('SPAN', (0, 0), (-1, 0)),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(amount_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#757575'),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    elements.append(Paragraph("Thank you for your payment!", footer_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

