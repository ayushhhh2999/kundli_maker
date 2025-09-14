import io
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from dotenv import load_dotenv
load_dotenv()  # must be called before os.getenv()

def generate_pdf(data: dict, logo_path: str = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#2E86C1"),
        alignment=1
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1F618D"),
        spaceAfter=6,
        spaceBefore=10
    )
    subheading_style = ParagraphStyle(
        "SubHeadingStyle",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=colors.HexColor("#117864"),
        spaceAfter=4,
        spaceBefore=6
    )
    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=16
    )

    story = []

    # Add logo if provided
    if logo_path:
        try:
            img = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 12))
        except Exception:
            story.append(Paragraph("⚠️ Logo not found", normal_style))

    # Title
    story.append(Paragraph("🔮 Kundli Report", title_style))
    story.append(Spacer(1, 20))

    def render_dict(d: dict, indent=0):
        """Recursively render dictionary with indentation and styles"""
        for key, value in d.items():
            if key.lower() == "status":
                continue  # skip status

            if isinstance(value, dict):
                story.append(Paragraph(" " * indent + f"<b>{key}</b>:", heading_style))
                render_dict(value, indent + 4)

            elif isinstance(value, list):
                story.append(Paragraph(" " * indent + f"<b>{key}</b>:", heading_style))
                for i, item in enumerate(value, start=1):
                    if isinstance(item, dict):
                        story.append(Paragraph(" " * (indent + 4) + f"• Item {i}:", subheading_style))
                        render_dict(item, indent + 8)
                    else:
                        story.append(Paragraph(" " * (indent + 4) + f"• {item}", normal_style))

            else:
                story.append(Paragraph(" " * indent + f"<b>{key}</b>: {value}", normal_style))
                story.append(Spacer(1, 4))

    # Render main data
    render_dict(data)

    # Footer
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "✨ Generated with ❤️ using Astrology App ✨",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#7D3C98"), alignment=1)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


import aiosmtplib
from email.message import EmailMessage

async def send_email(to_email: str, pdf_bytes: bytes):
    msg = EmailMessage()
    msg["From"] = "ayushsingh2999@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = "Your Kundli Report"

    msg.set_content("Attached is your Kundli PDF report.")

    # Attach PDF
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename="kundli_report.pdf")

    # Gmail SMTP (example)
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=os.getenv("GMAIL"),
        password=os.getenv("PASS"),  # ⚡ Use App Password, not raw Gmail password
    )
    
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
import time

def get_coordinates_str(location_name: str):
    geolocator = Nominatim(user_agent="my_app", timeout=10)  # timeout bada diya
    
    for attempt in range(3):  # 3 attempts karega
        try:
            location = geolocator.geocode(location_name)
            if location:
                return f"{location.latitude},{location.longitude}"
            else:
                return None
        except (GeocoderTimedOut, GeocoderUnavailable):
            time.sleep(2)  # wait then retry
    
    return None