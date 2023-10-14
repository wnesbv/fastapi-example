
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LikeBase(BaseModel):
    upvote: bool

class LikeChoose(LikeBase):
    created_at: datetime


class Like(LikeBase):
    like_item_id: int
    like_user_id: int
    like_user: list[int]
    like_item: list[int]

    class Config:
        from_attributes = True


# ...


class DislikeBase(BaseModel):
    downvote: bool


class DislikeChoose(DislikeBase):
    created_at: datetime


class Dislike(DislikeBase):
    dislike_item_id: int
    dislike_user_id: int
    dislike_user: list[int]
    dislike_item: list[int]

    class Config:
        from_attributes = True


from user.schemas import IUser
from item.schemas import Item

Like.update_forward_refs()
Dislike.update_forward_refs()