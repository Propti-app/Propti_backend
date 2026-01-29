# app/utils/pdf_generator.py
"""
PDF Receipt Generator for Propti
Cameroon-friendly receipt generation with FCFA currency
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime


def generate_payment_receipt(payment_data: dict) -> BytesIO:
    """
    Generate a professional payment receipt PDF
    
    Args:
        payment_data: Dictionary containing:
            - receipt_number: str
            - tenant_name: str
            - room_number: str
            - amount: float
            - payment_date: datetime
            - payment_method: str
            - period_start: date
            - period_end: date
            - remaining_balance: float
            - landlord_name: str
            - landlord_contact: str
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    # Create PDF
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # ===== HEADER =====
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, height - 2*cm, "PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 2.5*cm, "Propti Property Management")
    
    # Receipt number
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(width - 2*cm, height - 3.5*cm, f"Receipt No: {payment_data['receipt_number']}")
    
    # Date
    p.setFont("Helvetica", 10)
    payment_date = payment_data['payment_date']
    if isinstance(payment_date, str):
        date_str = payment_date.split('T')[0]
    else:
        date_str = payment_date.strftime('%d/%m/%Y')
    
    p.drawRightString(width - 2*cm, height - 4*cm, f"Date: {date_str}")
    
    # ===== DIVIDER LINE =====
    p.setStrokeColor(colors.HexColor('#4A5568'))
    p.setLineWidth(2)
    p.line(2*cm, height - 4.5*cm, width - 2*cm, height - 4.5*cm)
    
    # ===== TENANT INFORMATION =====
    y_position = height - 6*cm
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2*cm, y_position, "TENANT INFORMATION")
    
    y_position -= 0.8*cm
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y_position, f"Name: {payment_data['tenant_name']}")
    
    y_position -= 0.6*cm
    p.drawString(2*cm, y_position, f"Room: {payment_data['room_number']}")
    
    # ===== PAYMENT DETAILS =====
    y_position -= 1.5*cm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2*cm, y_position, "PAYMENT DETAILS")
    
    # Amount paid - Large and prominent
    y_position -= 1.2*cm
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor('#059669'))  # Green color
    amount_text = f"{int(payment_data['amount']):,} FCFA"
    p.drawString(2*cm, y_position, f"Amount Paid: {amount_text}")
    
    # Payment method
    y_position -= 0.8*cm
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.black)
    p.drawString(2*cm, y_position, f"Payment Method: {payment_data['payment_method']}")
    
    # Period covered
    y_position -= 0.6*cm
    period_start = payment_data.get('period_start', '')
    period_end = payment_data.get('period_end', '')
    
    if isinstance(period_start, str):
        period_start = period_start.split('T')[0] if 'T' in period_start else period_start
    if isinstance(period_end, str):
        period_end = period_end.split('T')[0] if 'T' in period_end else period_end
    
    p.drawString(2*cm, y_position, f"Period: {period_start} to {period_end}")
    
    # ===== BALANCE INFORMATION =====
    y_position -= 1.5*cm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2*cm, y_position, "BALANCE")
    
    y_position -= 0.8*cm
    remaining_balance = payment_data.get('remaining_balance', 0.0)
    
    if remaining_balance > 0:
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#DC2626'))  # Red color
        balance_text = f"{int(remaining_balance):,} FCFA"
        p.drawString(2*cm, y_position, f"Remaining Balance: {balance_text}")
        
        y_position -= 0.7*cm
        p.setFont("Helvetica-Oblique", 9)
        p.setFillColor(colors.HexColor('#7C2D12'))
        p.drawString(2*cm, y_position, "Status: PARTIALLY PAID")
    else:
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.HexColor('#059669'))  # Green color
        p.drawString(2*cm, y_position, "PAID IN FULL")
        
        y_position -= 0.7*cm
        p.setFont("Helvetica-Oblique", 9)
        p.setFillColor(colors.HexColor('#065F46'))
        p.drawString(2*cm, y_position, "Status: COMPLETE")
    
    # ===== DIVIDER LINE =====
    y_position -= 1*cm
    p.setStrokeColor(colors.HexColor('#4A5568'))
    p.setLineWidth(1)
    p.line(2*cm, y_position, width - 2*cm, y_position)
    
    # ===== LANDLORD INFORMATION =====
    y_position -= 1*cm
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.black)
    p.drawString(2*cm, y_position, "ISSUED BY")
    
    y_position -= 0.7*cm
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y_position, f"{payment_data['landlord_name']}")
    
    y_position -= 0.6*cm
    p.drawString(2*cm, y_position, f"Contact: {payment_data['landlord_contact']}")
    
    # ===== FOOTER =====
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(colors.HexColor('#6B7280'))
    footer_text = "This is a computer-generated receipt. Thank you for your payment."
    p.drawCentredString(width / 2, 2*cm, footer_text)
    
    p.setFont("Helvetica", 8)
    p.drawCentredString(width / 2, 1.5*cm, "Powered by Propti - Property Management Made Easy")
    
    # Save PDF
    p.showPage()
    p.save()
    
    # Reset buffer position
    buffer.seek(0)
    return buffer


def generate_financial_report(report_data: dict) -> BytesIO:
    """
    Generate a financial report PDF
    
    Args:
        report_data: Dictionary containing report metrics
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Header
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 2*cm, "FINANCIAL REPORT")
    
    p.setFont("Helvetica", 10)
    date_range = f"{report_data['start_date']} to {report_data['end_date']}"
    p.drawCentredString(width / 2, height - 2.7*cm, date_range)
    
    # Divider
    p.setLineWidth(2)
    p.line(2*cm, height - 3.2*cm, width - 2*cm, height - 3.2*cm)
    
    # Metrics
    y = height - 4.5*cm
    
    metrics = [
        ("Total Expected Rent", report_data['total_expected_rent']),
        ("Total Paid", report_data['total_paid']),
        ("Total Outstanding", report_data['total_outstanding']),
        ("Net Income", report_data['net_income'])
    ]
    
    for label, value in metrics:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(2*cm, y, f"{label}:")
        p.drawRightString(width - 2*cm, y, f"{int(value):,} FCFA")
        y -= 1*cm
    
    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, 2*cm, "Powered by Propti")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer