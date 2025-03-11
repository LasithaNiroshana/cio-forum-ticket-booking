from pydantic import BaseModel


class EmailRequest(BaseModel):
    email: str


class OTPConfirmation(BaseModel):
    email: str
    otp: str