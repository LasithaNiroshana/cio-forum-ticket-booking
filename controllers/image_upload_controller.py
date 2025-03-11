import base64
import logging
import os
import uuid
from models.response_model import error_response_model


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_image(base64_data: str, upload_path: str, old_image: str = '', file_name: str = None):
    try:
        allowed_file_formats = ['.jpg', '.jpeg', '.pdf']

        # Extract the file extension from the base64 data
        file_extension = '.' + base64_data.split(';')[0].split('/')[-1]

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

            # Decode the base64 data
            file_data = base64.b64decode(base64_data.split(',')[1])

            # Write the binary data to the file
            with open(file_location, "wb") as f:
                f.write(file_data)

            return file_location
        else:
            logger.error(f"Invalid file format: {file_extension}")
            return error_response_model(f"Invalid file format: {file_extension}", code=400)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return error_response_model(f"Error uploading file: {e}", code=500)