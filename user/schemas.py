
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, TypeAdapter


class UserBase(BaseModel):
    email: EmailStr


class UserRegister(UserBase):
    pass


class UserCreate(UserBase):
    created_at: datetime


class UserUpdate(BaseModel):
    name: str
    password: str
    modified_at: datetime


class GetUser(UserBase):
    id: int
    password: str
    email_verified: bool
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


# ...
class UiUser(UserBase):
    id: int

    class Config:
        from_attributes = True


class InItem(BaseModel):
    id: int
    title: str
    description: str
    owner_item_id: int

    class Config:
        from_attributes = True

# ...
class IUser(UserBase):
    id: int
    email_verified: bool
    is_active: bool
    is_admin: bool
    user_item: list[int]
    user_cmt: list[int]
    user_like: list[int]
    user_dislike: list[int]
    in_user: list[InItem]

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    password: str
    email_verified: bool
    is_active: bool
    is_admin: bool
    user_item: list[int]
    user_cmt: list[int]
    user_like: list[int]
    user_dislike: list[int]

    class Config:
        from_attributes = True


from item.schemas import Item
from comment.schemas import Comment
from vote.schemas import Like, Dislike


UiUser.update_forward_refs()
IUser.update_forward_refs()
User.update_forward_refs()
