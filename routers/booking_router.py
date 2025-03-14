from typing import Optional

from fastapi import APIRouter, Query, Request, Body
from controllers.booking_controller import reserve_forum_tickets, get_all_bookings, get_booking_by_id
from models.booking_model import BookingSchema

bookingRouter = APIRouter(
    prefix="/booking",
    tags=["Booking"],
)


@bookingRouter.post("/reserve-tickets")
async def reserve_tickets(
        request: Request,
        booking: BookingSchema = Body(...)):

    return await reserve_forum_tickets(request=request, booking_details=booking)


@bookingRouter.get("/get-booking/")
async def get_booking(booking_id: str = Query(..., description="The ID of the booking to retrieve")):
    return await get_booking_by_id(booking_id)


@bookingRouter.get("/get-all-bookings")
async def get_bookings():
    return await get_all_bookings()

