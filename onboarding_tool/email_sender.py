"""
E-Mail-Versand mit PDF-Anhang.
Unterstützt SMTP (Gmail, Outlook, eigener Server).
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Eure Agentur")


def _build_html_body(customer: dict, report_date: str) -> str:
    contact_name = customer.get("contact_name") or customer["name"]
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; color: #2C3E50; line-height: 1.6; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 30px; }}
    .header {{ background: #1A1A2E; color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
    .header h1 {{ margin: 0; font-size: 22px; }}
    .header p {{ margin: 5px 0 0; color: #BDC3C7; font-size: 14px; }}
    .body {{ background: #F9F9F9; padding: 30px; border-radius: 0 0 8px 8px; }}
    .highlight {{ background: #E94560; color: white; padding: 12px 20px;
                  border-radius: 5px; display: inline-block; margin: 15px 0; }}
    .footer {{ color: #7F8C8D; font-size: 12px; margin-top: 20px; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 5px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Onboarding Marktanalyse</h1>
      <p>{customer['name']} · {report_date}</p>
    </div>
    <div class="body">
      <p>Hallo {contact_name},</p>
      <p>
        anbei findet ihr eure persönliche <strong>Onboarding Marktanalyse</strong>
        für den Bereich <em>{customer['niche']}</em>.
      </p>
      <p>Der Report enthält:</p>
      <ul>
        <li>Demografisches & psychografisches Zielgruppenprofil</li>
        <li>Sprache & Tonalität eurer Zielgruppe</li>
        <li>Kauftrigger & Kaufsignale</li>
        <li>SEO-Analyse mit Keywords nach Intent</li>
        <li>Wettbewerber-Analyse (DE + International)</li>
        <li>Konkrete Video-Ideen je Funnel-Stufe</li>
      </ul>
      <div class="highlight">📄 Report im Anhang</div>
      <p>
        Bei Fragen stehen wir euch jederzeit zur Verfügung.
      </p>
      <p>Viele Grüße,<br><strong>{SENDER_NAME}</strong></p>
      <div class="footer">
        Diese E-Mail wurde automatisch generiert. · {datetime.now().strftime('%d.%m.%Y')}
      </div>
    </div>
  </div>
</body>
</html>
"""


def send_report(customer: dict, pdf_path: str, recipient_email: str = None) -> bool:
    """
    Sendet den PDF-Report per E-Mail an den Kunden.

    Args:
        customer: Kunden-Dict aus der Datenbank
        pdf_path: Pfad zur generierten PDF
        recipient_email: Überschreibt customer['contact_email'] falls angegeben

    Returns:
        True bei Erfolg, False bei Fehler
    """
    to_email = recipient_email or customer.get("contact_email", "")
    if not to_email:
        print("  ⚠️  Keine E-Mail-Adresse für Kunden hinterlegt.")
        return False

    if not SMTP_USER or not SMTP_PASSWORD:
        print("  ⚠️  SMTP_USER / SMTP_PASSWORD nicht in .env gesetzt.")
        return False

    if not os.path.exists(pdf_path):
        print(f"  ⚠️  PDF nicht gefunden: {pdf_path}")
        return False

    try:
        report_date = datetime.now().strftime("%d.%m.%Y")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Eure Onboarding Marktanalyse – {customer['name']} · {report_date}"
        msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg["To"] = to_email

        # HTML Body
        html_body = _build_html_body(customer, report_date)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # PDF Anhang
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(pdf_data)
        encoders.encode_base64(attachment)
        pdf_filename = os.path.basename(pdf_path)
        attachment.add_header(
            "Content-Disposition", "attachment",
            filename=pdf_filename
        )
        msg.attach(attachment)

        # Senden
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"  ✅ E-Mail gesendet an: {to_email}")
        return True

    except Exception as e:
        print(f"  ❌ E-Mail Fehler: {e}")
        return False
