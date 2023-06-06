
from datetime import datetime

from pydantic import BaseModel
from fastapi import UploadFile




class ImportCSV(BaseModel):
    id: int
    title: str
    description: str
    image_url: str
    created_at: datetime = None
    owner_item_id: int


class ExportCSV(ImportCSV):
    modified_at: datetime = None


class BaseCSV(ExportCSV):
    item_user: list["User"] = []
    item_cmt: list["Comment"] = []
    item_like: list["Like"] = []
    item_dislike: list["Dislike"] = []

    class Config:
        orm_mode = True


from user.schemas import User
from comment.schemas import Comment
from vote.schemas import Like, Dislike

BaseCSV.update_forward_refs()