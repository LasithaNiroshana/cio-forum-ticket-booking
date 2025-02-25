from fastapi import APIRouter, Depends, Query, UploadFile, File, Request
from controllers.email_controller import send_email_with_otp, confirm_email
from models.booking_model import OTPConfirmation

emailRouter = APIRouter(
    prefix="/email",
    tags=["Emails"],
)


@emailRouter.post("/send-email-otp")
async def reserve_tickets(email: str):
    return send_email_with_otp(email)


@emailRouter.post("/verify-email")
async def verify_email(confirmation: OTPConfirmation):
    return await confirm_email(confirmation)