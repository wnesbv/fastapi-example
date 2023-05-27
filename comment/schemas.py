
from datetime import datetime, timedelta
from pydantic import BaseModel


class CommentBase(BaseModel):
    opinion: str


class CommentCreate(CommentBase):
    cmt_user_id: int
    cmt_item_id: int
    created_at: datetime = None


class CommentUpdate(CommentBase):
    opinion: str
    modified_at: datetime = None


class Comment(CommentBase):
    id: int
    cmt_user: list["User"] = []
    cmt_item: list["Item"] = []

    class Config:
        orm_mode = True


from user.schemas import User
from item.schemas import Item

Comment.update_forward_refs()
