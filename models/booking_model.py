from typing import Optional

from pydantic import BaseModel, Field
from enum import Enum


# class PaymentStatus(int, Enum):
#     NOT_PAID = 0
#     PAID = 1


class BookingSchema(BaseModel):
    _id: Optional[str] = None
    full_name: str = Field(...)
    email: str = Field(...)
    phone_number: str = Field(...)
    ticket_count: int = Field(...)
    amount: int = Field(...)
    bank_slip: Optional[str] = None
    paid_status: int = Field(...)  # not paid=0 paid=1
    email_confirmed: Optional[int] = 0  # not confirmed=0 confirmed=1

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "65f8c2a1e6b7c927d5f3a6b9",
                "full_name": "John Doe",
                "emails": "johndoe@gmail.com",
                "phone_number": "0711231234",
                "ticket_count": 2,
                "amount": 2000,
                "bank_slip": "https://www.eticketing.com/images/000123",
                "paid_status": 1,
                "email_confirmed": 1
            }
        }


class OTPConfirmation(BaseModel):
    email: str
    otp: str


