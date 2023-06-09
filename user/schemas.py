
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserRegister(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
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
        orm_mode = True


# ...
class UiUser(UserBase):
    id: int

    class Config:
        orm_mode = True


# ...
class IUser(UserBase):
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


class User(UserBase):
    id: int
    password: str
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


UiUser.update_forward_refs()
IUser.update_forward_refs()
User.update_forward_refs()

