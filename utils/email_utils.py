import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Load config from environment
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "TOPSIS Result")

def send_email(data: pd.DataFrame, recipient_email: str):
    """
    Sends an email with the TOPSIS result as a CSV attachment.
    If no recipient email is provided, this function skips sending.
    """
    if not recipient_email:
        return

    try:
        # Create email container
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = EMAIL_SUBJECT

        # Email body
        body = "Dear User,\n\nAttached is the TOPSIS result CSV file you requested.\n\nBest regards,\nPulkit Arora"
        msg.attach(MIMEText(body, 'plain'))

        # Prepare data + CSV attachment
        data_with_rank = data.copy()
        data_with_rank['Rank'] = data['Custom Score'].rank(ascending=False)
        result_csv = data_with_rank.to_csv(index=False)

        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(result_csv.encode('utf-8'))
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename='result_with_rank.csv')
        msg.attach(attachment)

        # Send email via Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()

        print("[INFO] Email sent successfully.")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
