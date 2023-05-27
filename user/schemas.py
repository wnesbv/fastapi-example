
from datetime import datetime, timedelta
from typing import List, Any, Dict, Literal

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserRegister(UserBase):
    password: str


class UserCreate(UserBase):
    password: str
    created_at: datetime = None


class UserUpdate(UserBase):
    name: str | None = None
    password: str | None = None
    modified_at: datetime = None


class User(UserBase):
    id: int
    email_verified: bool
    is_active: bool
    is_admin: bool
    user_item: list["Item"] = []
    user_cmt: list["Comment"] = []
    user_like: list["Like"] = []
    user_dislike: list["Dislike"] = []

    class Config:
        orm_mode = True


from item.schemas import Item
from comment.schemas import Comment
from vote.schemas import Like, Dislike

User.update_forward_refs()

