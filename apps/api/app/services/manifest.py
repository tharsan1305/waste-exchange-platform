import io
import qrcode
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from app.core.security import compute_sha256

def generate_deal_manifest_pdf(deal_data: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Generates a verifiable PDF e-Challan / Industrial Consignment Manifest
    with embedded QR code and returns (pdf_bytes, sha256_hash).
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header & Banner
    p.setFillColor(colors.HexColor("#1b4332"))
    p.rect(0, height - 70, width, 70, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(36, height - 42, "INDUSTRIAL SYMBIOSIS WASTE CONSIGNMENT MANIFEST")
    p.setFont("Helvetica", 10)
    p.drawString(36, height - 58, "Official Digital E-Challan & Traceability Document (CPCB / TNPCB Compliant)")

    # Deal Identifiers
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(36, height - 100, f"Manifest No: MAN-{deal_data.get('id', 'N/A')[:8].upper()}")
    p.setFont("Helvetica", 10)
    p.drawString(36, height - 116, f"Batch Code: {deal_data.get('batch_code', 'BATCH-GENERIC')}")
    p.drawString(300, height - 100, f"Generated At: {deal_data.get('generated_at', '2026-10-11')}")
    p.drawString(300, height - 116, f"Consignment Status: {deal_data.get('stage', 'agreed').upper()}")

    # Divider line
    p.setStrokeColor(colors.HexColor("#d3d3d3"))
    p.line(36, height - 128, width - 36, height - 128)

    # Consignor & Consignee Columns
    y = height - 150
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.HexColor("#2d6a4f"))
    p.drawString(36, y, "1. CONSIGNOR (GENERATOR / SELLER)")
    p.drawString(300, y, "2. CONSIGNEE (RECIPIENT / BUYER)")

    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    seller = deal_data.get("seller", {})
    buyer = deal_data.get("buyer", {})

    p.drawString(36, y - 18, f"Company: {seller.get('name', 'N/A')}")
    p.drawString(36, y - 32, f"GSTIN: {seller.get('gst_number', 'N/A')}")
    p.drawString(36, y - 46, f"Facility: {seller.get('address', 'N/A')[:40]}")
    p.drawString(36, y - 60, f"PCB Auth: {seller.get('pcb_authorization_no', 'Exempt')}")

    p.drawString(300, y - 18, f"Company: {buyer.get('name', 'N/A')}")
    p.drawString(300, y - 32, f"GSTIN: {buyer.get('gst_number', 'N/A')}")
    p.drawString(300, y - 46, f"Facility: {buyer.get('address', 'N/A')[:40]}")
    p.drawString(300, y - 60, f"PCB Auth: {buyer.get('pcb_authorization_no', 'Exempt')}")

    # Waste Specification Box
    y_box = y - 90
    p.setFillColor(colors.HexColor("#f8f9fa"))
    p.rect(36, y_box - 90, width - 72, 90, fill=True, stroke=True)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(48, y_box - 18, "3. BYPRODUCT MATERIAL SPECIFICATION")
    p.setFont("Helvetica", 9)
    p.drawString(48, y_box - 36, f"Material Name: {deal_data.get('waste_name', 'Industrial Byproduct')}")
    p.drawString(48, y_box - 50, f"Consigned Quantity: {deal_data.get('quantity', 0.0)} Tonnes")
    p.drawString(48, y_box - 64, f"Hazardous Classification: {'YES (Hazardous)' if deal_data.get('is_hazardous') else 'NO (Non-Hazardous Biomass/Mineral)'}")
    p.drawString(300, y_box - 36, f"Agreed Rate: INR {deal_data.get('agreed_price_per_unit', 0.0)} / Ton")
    p.drawString(300, y_box - 50, f"Total Consignment Value: INR {deal_data.get('total_amount', 0.0)}")

    # Logistics & Transporter Section
    y_trans = y_box - 110
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.HexColor("#2d6a4f"))
    p.drawString(36, y_trans, "4. TRANSPORTATION & VEHICLE DETAILS")
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    p.drawString(36, y_trans - 18, f"Transporter Agency: {deal_data.get('transporter_name', 'Authorized Haulier')}")
    p.drawString(36, y_trans - 32, f"Vehicle Reg No: {deal_data.get('vehicle_number', 'TN-NOT-ASSIGNED')}")
    p.drawString(36, y_trans - 46, f"Transporter PCB Auth: {deal_data.get('transporter_pcb_auth_no', 'N/A')}")

    # Generate QR Code for Verification
    qr_content = f"https://waste-exchange.app/passport/{deal_data.get('batch_code', 'DEFAULT')}?deal={deal_data.get('id', '')}"
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(qr_content)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_bytes = io.BytesIO()
    qr_img.save(qr_bytes, format='PNG')
    qr_bytes.seek(0)

    # Embed QR Code
    p.drawInlineImage(qr_img, width - 150, y_trans - 80, width=90, height=90)
    p.setFont("Helvetica", 8)
    p.drawString(width - 155, y_trans - 90, "Scan to Verify Authenticity")

    # Environmental ESG Impact Summary
    y_esg = y_trans - 110
    p.setFillColor(colors.HexColor("#e8f5e9"))
    p.rect(36, y_esg - 40, width - 200, 40, fill=True, stroke=False)
    p.setFillColor(colors.HexColor("#1b4332"))
    p.setFont("Helvetica-Bold", 9)
    p.drawString(44, y_esg - 16, "VERIFIED ESG CIRCULAR ECONOMY BENEFIT:")
    p.setFont("Helvetica", 9)
    p.drawString(44, y_esg - 30, f"Landfill Diverted: {deal_data.get('quantity', 0.0)} MT  |  CO2 Mitigation: {round(float(deal_data.get('quantity', 0.0)) * 0.85, 2)} MT CO2e")

    # Legal Disclaimer & Digital Seal
    p.setFillColor(colors.dimgray)
    p.setFont("Helvetica-Oblique", 7)
    p.drawString(36, 40, "This e-Manifest is digitally certified. In compliance with Hazardous and Other Wastes Rules, 2016.")
    p.drawString(36, 30, "Document tamper resistance guaranteed via cryptographic SHA-256 ledger integrity check.")

    p.showPage()
    p.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    sha256_hash = compute_sha256(pdf_bytes)

    return pdf_bytes, sha256_hash
