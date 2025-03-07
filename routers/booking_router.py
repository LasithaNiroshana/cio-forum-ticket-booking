from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File, Request, Form
from controllers.booking_controller import reserve_forum_tickets, get_all_bookings, get_booking_by_id
from models.booking_model import BookingSchema

bookingRouter = APIRouter(
    prefix="/booking",
    tags=["Booking"],
)


@bookingRouter.post("/reserve-tickets")
async def reserve_tickets(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        phone_number: str = Form(...),
        ticket_count: int = Form(...),
        amount: int = Form(...),
        paid_status: int = Form(...),
        email_confirmed: int = Form(...),
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

    return await reserve_forum_tickets(request=request, booking_details=booking_details, bank_slip_file=bank_slip_file)


@bookingRouter.get("/get-booking/")
async def get_booking(booking_id: str = Query(..., description="The ID of the booking to retrieve")):
    return await get_booking_by_id(booking_id)


@bookingRouter.get("/get-all-bookings")
async def get_bookings():
    return await get_all_bookings()

