
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
    created_at: datetime


class ItemUpdate(BaseModel):
    title: str
    description: str
    modified_at: datetime


class ItemImgUpdate(ItemBase):
    modified_at: datetime


class Item(ItemBase):
    id: int
    image_url: UploadFile | None = None
    owner_item_id: int
    item_user: list["User"] = []
    item_cmt: list["Comment"] | None = None
    item_like: list["Like"] | None = None
    item_dislike: list["Dislike"] | None = None

    class Config:
        orm_mode = True


from user.schemas import User
from comment.schemas import Comment
from vote.schemas import Like, Dislike

Item.update_forward_refs()
