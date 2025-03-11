from fastapi import APIRouter, Depends, Query, UploadFile, File, Request, Form
from controllers.email_controller import send_email_with_otp, confirm_email
from models.email_model import EmailRequest, OTPConfirmation

emailRouter = APIRouter(
    prefix="/email",
    tags=["Emails"],
)


@emailRouter.post("/send-email-otp")
async def reserve_tickets(email_request: EmailRequest):
    return send_email_with_otp(email_request.email)


@emailRouter.post("/verify-email")
async def verify_email(confirmation: OTPConfirmation):
    return await confirm_email(confirmation)