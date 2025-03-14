from pydantic import BaseModel, Field, field_validator
from typing import Optional

class BookingSchema(BaseModel):
    _id: Optional[str] = None
    full_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
    ticket_count: int = Field(...)
    amount: int = Field(...)
    bank_slip: Optional[str] = None
    paid_status: int = Field(...)  # not paid=0 paid=1
    email_confirmed: int = Field(...)  # not confirmed=0 confirmed=1

    @field_validator("bank_slip")
    def validate_bank_slip(cls, value):
        if value is None:
            return value

        value = value.strip()  # Remove leading/trailing whitespace

        print(f"Validating bank_slip: {value}")  # Debugging

        # Allow URLs, base64-encoded images, or base64-encoded PDFs
        if (
            value==""
            or value.startswith("http://")
            or value.startswith("https://")
            or value.startswith("data:image/")  # Allow base64-encoded images
            or value.startswith("data:application/pdf;base64,")  # Allow base64-encoded PDFs
        ):
            print("Validation passed")  # Debugging
            return value
        else:
            print("Validation failed")  # Debugging
            raise ValueError("Bank_slip must be a URL, a base64-encoded image, or a base64-encoded PDF")

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "65f8c2a1e6b7c927d5f3a6b9",
                "full_name": "John Doe",
                "email": "johndoe@gmail.com",
                "phone_number": "0711231234",
                "ticket_count": 2,
                "amount": 2000,
                "bank_slip": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a...",
                "paid_status": 1,
                "email_confirmed": 1
            }
        }