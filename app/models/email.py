from fastapi import Form
from pydantic import BaseModel, EmailStr


class SingleEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    salutation: str   # e.g. "Dear John" — sent as-is
    body: str


class BulkEmailRow(BaseModel):
    name: str
    email: EmailStr


class BulkEmailRequest(BaseModel):
    subject: str
    body: str
    delay: float = 1.0   # seconds between each email

    @classmethod
    def as_form(
        cls,
        subject: str = Form(..., description="Email subject"),
        body: str = Form(..., description="Email body (salutation will be prepended per recipient)"),
        delay: float = Form(1.0, description="Delay in seconds between each email"),
    ) -> "BulkEmailRequest":
        return cls(subject=subject, body=body, delay=delay)
