
from typing import List, Any, Dict
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginDetails(BaseModel):
    email: str
    password: str


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]


class ResetPasswordDetails(BaseModel):
    password: str
