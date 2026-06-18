import os
import smtplib
import imaplib
from dotenv import load_dotenv


load_dotenv()

EMAIL_USER=os.getenv("GMAIL_USER")
EMAIL_PASSWORD=os.getenv("GMAIL_PASSWORD")


def get_smtp_connection():
    """Returns an authenticated SMTP connection to send emails."""
    try:
        # Gmail uses SMTP server with port 465 (SSL) or 587 (TLS). We are using TLS.
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls() # To secure the connection
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        return server
    except Exception as e:
        print(f"SMTP Authentication Error: {e}")
        return None
    


def get_imap_connection():
    """Returns an authenticated IMAP connection to read emails."""
    try:
        # Gmail's IMAP server runs on SSL (Port 993)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        return mail
    except Exception as e:
        print(f"IMAP Authentication Error: {e}")
        return None