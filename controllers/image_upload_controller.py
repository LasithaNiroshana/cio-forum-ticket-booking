import base64
import logging
import os
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException

from models.response_model import error_response_model


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_image(base64_data: str, upload_path: str, old_image: str = '', file_name: str = None):
    try:
        allowed_file_formats = ['.png', '.jpg', '.jpeg', '.pdf']

        # Extract the file extension from the base64 data
        file_extension = '.' + base64_data.split(';')[0].split('/')[-1]

        # Validate file format
        if file_extension.lower() not in allowed_file_formats:
            logger.error(f"Invalid file format: {file_extension}")
            raise ValueError(f"Invalid file format: {file_extension}")

        # Delete old image if it exists
        if old_image and os.path.exists(old_image):
            os.remove(old_image)

        # Create upload directory if it doesn't exist
        if not os.path.isdir(upload_path):
            os.makedirs(upload_path)

        # Generate file name
        if file_name:
            filename = file_name + file_extension
        else:
            filename = f"{uuid.uuid4().hex[:20].upper()}{file_extension}"

        file_location = os.path.join(upload_path, filename)

        # Decode the base64 data
        file_data = base64.b64decode(base64_data.split(',')[1])

        # Write the binary data to the file
        with open(file_location, "wb") as f:
            f.write(file_data)

        return file_location

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")