import os
import uuid
from datetime import datetime
import logging
from bson import ObjectId
from fastapi import UploadFile, Request
from configparser import ConfigParser

from models.booking_model import BookingSchema
from models.response_model import response_model, error_response_model
from database.database import get_db

config = ConfigParser()
config.read(".cfg")
BASE_URL = config.get("ENVIRONMENT", "BASE_URL", fallback="http://127.0.0.1:8000/".rstrip("/"))

UPLOAD_DIR = "public/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reserve_forum_tickets(request: Request, booking_details: BookingSchema, bank_slip_file: UploadFile = None):
    try:
        logger.info(f"Reserving tickets for: {booking_details.full_name}")
        db = await get_db()

        if booking_details.paid_status == 1 and not bank_slip_file:
            return error_response_model("Bank slip file is required when status is paid.", code=400)
        bank_slip_url = None

        if bank_slip_file:
            # Generate a unique filename based on user's full name and timestamp
            file_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{booking_details.full_name}"
            file_location = upload_image(bank_slip_file, UPLOAD_DIR, file_name=file_name)

            if not file_location:
                return error_response_model("Failed to upload bank slip.", code=500)

            base_url = str(request.base_url).rstrip("/")
            bank_slip_path = "/" + file_location.replace("public\\", "").replace("\\", "/")
            bank_slip_url = base_url + bank_slip_path

        # Prepare the booking data
        booking_data = booking_details.dict()
        booking_data["created_at"] = datetime.utcnow()
        booking_data["bank_slip"] = bank_slip_url

        # Save the booking to the database
        result = await db["bookings"].insert_one(booking_data)

        if result.inserted_id:
            logger.info(f"Booking saved with ID: {result.inserted_id}")
            booking_data["_id"] = str(result.inserted_id)
            return response_model(booking_data, "Tickets reserved successfully.")
        else:
            logger.error("Failed to save booking to the database.")
            return error_response_model("Failed to reserve tickets.", code=500)

    except Exception as e:
        logger.error(f"Error reserving tickets: {e}")
        return error_response_model("An error occurred while reserving tickets.", code=500)


def upload_image(file: UploadFile, upload_path: str, old_image: str = '', file_name: str = None):
    try:
        allowed_file_formats = ['.jpg', '.jpeg', '.pdf']
        _, file_extension = os.path.splitext(file.filename)

        if file_extension.lower() in allowed_file_formats:
            if old_image and os.path.exists(old_image):
                os.remove(old_image)

            if not os.path.isdir(upload_path):
                os.makedirs(upload_path)

            if file_name:
                filename = file_name + file_extension
            else:
                filename = f"{uuid.uuid4().hex[:20].upper()}{file_extension}"

            file_location = os.path.join(upload_path, filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())

            return file_location

        else:
            print(f"Invalid image format: {file_extension}")
        return False

    except Exception as e:
        # Handle cases where file upload fails
        print(f"Error uploading video: {e}")
        return False
