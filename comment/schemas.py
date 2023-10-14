
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CommentBase(BaseModel):
    opinion_expressed: str


class CmtCreate(CommentBase):
    created_at: datetime


class CmtUpdate(CommentBase):
    modified_at: datetime


class CmtUser(CommentBase):
    id: int
    cmt_user_id: int
    cmt_item_id: int

    class Config:
        from_attributes = True


class Comment(CommentBase):
    id: int
    cmt_user_id: int
    cmt_item_id: int
    cmt_user: list[int]
    cmt_item: list[int]

    class Config:
        from_attributes = True


from user.schemas import UiUser
from item.schemas import UiItem

Comment.update_forward_refs()
