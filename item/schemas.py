from datetime import datetime

from pydantic import BaseModel
from fastapi import UploadFile


class ItemBase(BaseModel):
    title: str
    description: str


class ImgDel(BaseModel):
    image_url: UploadFile
    modified_at: datetime


class ItemCreate(ItemBase):
    image_url: UploadFile


class ItemUpdate(ItemBase):
    image_url: str


class ListItem(ItemBase):
    id: int
    image_url: str | None = None
    owner_item_id: int
    created_at: datetime
    modified_at: datetime | None = None

    class Config:
        orm_mode = True


class ApiListItem(ItemBase):
    id: int
    title: str
    description: str
    image_url: str | None = None

    class Config:
        orm_mode = True


# ...
class UiItem(ItemBase):
    id: int
    image_url: UploadFile | None = None
    owner_item_id: int

    class Config:
        orm_mode = True


# ...
class Item(ItemBase):
    id: int
    image_url: UploadFile | None = None
    owner_item_id: int
    item_user: list["IUser"] = []
    item_cmt: list["Comment"] = []
    item_like: list["Like"] = []
    item_dislike: list["Dislike"] = []

    class Config:
        orm_mode = True


from user.schemas import IUser
from comment.schemas import Comment
from vote.schemas import Like, Dislike


UiItem.update_forward_refs()
Item.update_forward_refs()
