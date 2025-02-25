from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Request
from controllers.booking_controller import reserve_forum_tickets
from models.booking_model import BookingSchema

bookingRouter = APIRouter(
    prefix="/booking",
    tags=["Booking"],
)


@bookingRouter.post("/reserve-tickets")
async def reserve_tickets(
        request: Request,
        full_name: str,
        email: str,
        phone_number: str,
        ticket_count: int,
        amount: int,
        paid_status: int,
        email_confirmed: int,
        bank_slip_file: Optional[UploadFile] = File(None)):
    booking_details = BookingSchema(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        ticket_count=ticket_count,
        amount=amount,
        paid_status=paid_status,
        email_confirmed=email_confirmed
    )

    return await reserve_forum_tickets(booking_details=booking_details, bank_slip_file=bank_slip_file, request=request)
