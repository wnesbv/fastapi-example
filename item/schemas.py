
from datetime import datetime, timedelta
from typing import List, Any, Dict

from pydantic import BaseModel
from fastapi import UploadFile


class ItemBase(BaseModel):
    title: str
    image_url: str | None = None
    description: str | None = None


class ItemCreate(ItemBase):
    created_at: datetime | None = None


class ItemUpdate(ItemBase):
    modified_at: datetime | None = None


class Item(ItemBase):
    id: int
    owner_item_id: int
    item_user: list["User"] = []
    item_cmt: list["Comment"] = []
    item_like: list["Like"] = []
    item_dislike: list["Dislike"] = []

    class Config:
        orm_mode = True


from user.schemas import User
from comment.schemas import Comment
from vote.schemas import Like, Dislike

Item.update_forward_refs()
