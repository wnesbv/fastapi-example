
from datetime import datetime
from pydantic import BaseModel


class CommentBase(BaseModel):
    opinion_expressed: str


class CmtCreate(CommentBase):
    created_at: datetime = None


class CmtUpdate(CommentBase):
    modified_at: datetime = None


class Comment(CommentBase):
    id: int
    cmt_user_id: int
    cmt_item_id: int
    cmt_user: list["User"] = []
    cmt_item: list["Item"] = []

    class Config:
        orm_mode = True


from user.schemas import User
from item.schemas import Item

Comment.update_forward_refs()
