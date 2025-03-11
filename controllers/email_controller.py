import random
import smtplib
import random
import string
import os
import time
from typing import Dict
import re

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser

from models.email_model import OTPConfirmation
from models.response_model import response_model, error_response_model

config = ConfigParser()
config.read(".cfg")

SMTP_HOST = config.get("SMTP", "HOST")
SMTP_PORT = config.getint("SMTP", "PORT")
SMTP_ENCRYPT = config.get("SMTP", "ENCRYPT")
SENDER_MAIL = config.get("SMTP", "SENDER_MAIL")
SENDER_PW = config.get("SMTP", "SENDER_PW")

otp_store: Dict[str, Dict[str, any]] = {}

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def validate_email(email):
    """Validate the email address format."""
    return re.match(EMAIL_REGEX, email) is not None


def generate_otp(length=6):
    """Generate a random OTP of given length"""
    characters = string.digits
    otp = ''.join(random.choice(characters) for i in range(length))
    return otp


def send_email_with_otp(recipient_email):
    """Send an OTP email to the user"""
    try:
        if not validate_email(recipient_email):
            print(f"Invalid email address: {recipient_email}")
            return error_response_model("Invalid email address format.", code=400)

        otp = generate_otp()
        otp_store[recipient_email] = {"otp": otp, "expires_at": time.time() + 300}
        msg = MIMEMultipart()
        msg['From'] = SENDER_MAIL
        msg['To'] = recipient_email
        msg['Subject'] = 'Email Confirmation - OTP'

        body = f"Your OTP code for email confirmation is: {otp}. It will expire in 5 minutes."
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) if SMTP_ENCRYPT.upper() == 'SSL' else smtplib.SMTP(SMTP_HOST,
                                                                                                           SMTP_PORT)
        server.login(SENDER_MAIL, SENDER_PW)

        server.sendmail(SENDER_MAIL, recipient_email, msg.as_string())
        server.quit()

        print(f"OTP sent to {recipient_email}")
        return response_model({"email": f"{recipient_email}"}, f"OTP sent to {recipient_email}")

    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return error_response_model(f"An error occurred while sending email: {e}", code=500)


async def confirm_email(confirmation: OTPConfirmation):
    email = confirmation.email
    entered_otp = confirmation.otp

    if email not in otp_store:
        return error_response_model("Cannot find email", code=400)

    otp_data = otp_store[email]
    stored_otp = otp_data["otp"]
    otp_expiry = otp_data["expires_at"]

    if entered_otp != stored_otp:
        return error_response_model("Invalid OTP", code=400)

    if time.time() > otp_expiry:
        del otp_store[email]  # Remove expired OTP
        return error_response_model("OTP has expired", code=400)

    if entered_otp != stored_otp:
        raise error_response_model("OTP not found", code=400)

    del otp_store[email]
    return response_model({"success_status": 1}, "Email confirmed successfully!")


async def send_booking_email(recipient_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_MAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        if SMTP_ENCRYPT.upper() == 'SSL':
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

        server.login(SENDER_MAIL, SENDER_PW)
        server.sendmail(SENDER_MAIL, recipient_email, msg.as_string())
        server.quit()

    except Exception as e:
        return error_response_model(f"Failed to send email: {e}", code=500)
