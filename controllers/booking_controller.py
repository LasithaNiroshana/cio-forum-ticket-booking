import base64
import os
import uuid
from datetime import datetime, timezone
import logging
from typing import Optional

from bson import ObjectId
from fastapi import UploadFile, Request, HTTPException
from configparser import ConfigParser

from controllers.email_controller import send_booking_email
from models.booking_model import BookingSchema
from models.response_model import response_model, error_response_model
from database.database import get_db
from controllers.image_upload_controller import upload_image

config = ConfigParser()
config.read(".cfg")
BASE_URL = config.get("ENVIRONMENT", "BASE_URL", fallback="http://127.0.0.1:8000/".rstrip("/"))

UPLOAD_DIR = "public/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reserve_forum_tickets(request: Request, booking_details):
    try:
        db = await get_db()

        # Check if email is not confirmed
        if booking_details.email_confirmed == 0:
            return error_response_model("Email address is not verified!.", code=400)

        base_url = str(request.base_url).rstrip("/")
        bank_slip_url = None

        # Handle bank slip file upload only if paid_status is 1
        if booking_details.paid_status == 1:
            if not booking_details.bank_slip:
                logger.error("Bank slip file is required when status is paid.")
                return error_response_model("Bank slip file is required when status is paid.", code=400)

            # Validate base64 data
            if not booking_details.bank_slip.startswith("data:image/"):
                logger.error("Invalid base64 image data.")
                return error_response_model("Invalid base64 image data.", code=400)

            logger.info("Received bank slip file as base64 data.")
            file_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{booking_details.full_name.strip().replace(' ', '_')}"
            file_location = upload_image(booking_details.bank_slip, UPLOAD_DIR, file_name=file_name)

            if not file_location:
                return error_response_model("Failed to upload bank slip.", code=500)

            bank_slip_path = "/" + file_location.replace("public\\", "").replace("\\", "/")
            bank_slip_url = base_url + bank_slip_path

        # Prepare the booking data
        booking_data = booking_details.model_dump()
        booking_data["created_at"] = datetime.now(timezone.utc)
        booking_data["bank_slip"] = bank_slip_url

        result = await db["bookings"].insert_one(booking_data)

        if result.inserted_id:
            booking_data["_id"] = str(result.inserted_id)

            # Send email to the user based on paid_status
            if booking_details.paid_status == 1:
                email_subject = "Payment Done for Booking"
                email_body = f"""
                    Dear {booking_details.full_name},

                    Your payment for the booking has been successfully processed. Below are your booking details:

                    - Booking ID: {result.inserted_id}
                    - Full Name: {booking_details.full_name}
                    - Email: {booking_details.email}
                    - Phone Number: {booking_details.phone_number}
                    - Ticket Count: {booking_details.ticket_count}
                    - Amount: {booking_details.amount}
                    - Bank Slip: {bank_slip_url}

                    Thank you for choosing our service!

                    Best regards,
                    Your Booking Team
                """
            else:
                payment_upload_link = f"{base_url}/upload-payment-slip?booking_id={result.inserted_id}"
                email_subject = "Payment Pending for Booking"
                email_body = f"""
                    Dear {booking_details.full_name},

                    Your booking has been successfully created. However, the payment is still pending. Please upload your payment slip using the link below:

                    Payment Slip Upload Link: {payment_upload_link}

                    Below are your booking details:

                    - Booking ID: {result.inserted_id}
                    - Full Name: {booking_details.full_name}
                    - Email: {booking_details.email}
                    - Phone Number: {booking_details.phone_number}
                    - Ticket Count: {booking_details.ticket_count}
                    - Amount: {booking_details.amount}

                    Thank you for choosing our service!

                    Best regards,
                    Your Booking Team
                """

            # Send the email
            await send_booking_email(booking_details.email, email_subject, email_body)

            return response_model(booking_data, "Tickets reserved successfully.")
        else:
            return error_response_model("Failed to reserve tickets.", code=500)

    except Exception as e:
        logger.error(f"An error occurred while reserving tickets: {e}", exc_info=True)
        return error_response_model(f"An error occurred while reserving tickets: {str(e)}", code=500)


async def get_booking_by_id(booking_id: str):
    try:
        db = await get_db()
        booking = await db["bookings"].find_one({"_id": ObjectId(booking_id)})

        if booking:
            booking["_id"] = str(booking["_id"]) if "_id" in booking else None
            booking.setdefault("email_confirmed", 0)
            booking.setdefault("bank_slip", None)
            booking.setdefault("created_at", None)

            return response_model(BookingSchema(**booking), "Booking details retrieved successfully.")
        else:
            return error_response_model("Booking not found.", code=404)

    except Exception as e:
        return error_response_model(f"An error occurred while fetching the booking: {e}", code=500)


async def get_all_bookings():
    try:
        db = await get_db()
        bookings = await db["bookings"].find().to_list(length=None)
        booking_list = []
        for booking in bookings:
            # print("Raw booking document:", booking)
            booking["_id"] = str(booking["_id"])
            # print("Booking after _id conversion:", booking)
            booking.setdefault("email_confirmed", 0)
            booking.setdefault("bank_slip", None)
            booking.setdefault("created_at", None)

            booking_list.append(booking)
        return response_model(booking_list, "All bookings retrieved successfully.")

    except Exception as e:
        return error_response_model(f"An error occurred while fetching bookings: {e}", code=500)
