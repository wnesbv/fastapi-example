
from __future__ import annotations
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, FilePath
from fastapi import UploadFile


class ItemBase(BaseModel):
    title: str
    description: str


class ImgDel(BaseModel):
    modified_at: datetime


class ItemCreate(ItemBase):
    image_url: UploadFile


class ItemUpdate(ItemBase):
    image_url: FilePath


class ListItem(ItemBase):
    id: int
    image_url: str | None = None
    owner_item_id: int
    created_at: datetime
    modified_at: datetime | None = None

    class Config:
        from_attributes = True


class ApiListItem(ItemBase):
    id: int
    title: str
    description: str
    image_url: str | None = None

    class Config:
        from_attributes = True


# ...
class UiItem(ItemBase):
    id: int
    image_url: UploadFile | None = None
    owner_item_id: int

    class Config:
        from_attributes = True


# ...
class Item(ItemBase):
    id: int
    image_url: UploadFile | None = None
    owner_item_id: int
    item_user: list[int]
    item_cmt: list[int]
    item_like: list[int]
    item_dislike: list[int]

    class Config:
        from_attributes = True


from user.schemas import IUser
from comment.schemas import Comment
from vote.schemas import Like, Dislike


UiItem.update_forward_refs()
Item.update_forward_refs()
