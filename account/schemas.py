from typing import Any
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginDetails(BaseModel):
    email: str
    password: str


class EmailSchema(BaseModel):
    email: list[EmailStr]
    body: dict[str, Any]


class ResetPasswordDetails(BaseModel):
    password: str
