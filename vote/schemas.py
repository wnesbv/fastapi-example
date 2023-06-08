
from datetime import datetime

from pydantic import BaseModel


class LikeBase(BaseModel):
    upvote: bool

class LikeChoose(LikeBase):
    created_at: datetime


class Like(LikeBase):
    like_item_id: int
    like_user_id: int
    like_user: list["IUser"] = []
    like_item: list["Item"] = []

    class Config:
        orm_mode = True


# ...


class DislikeBase(BaseModel):
    downvote: bool


class DislikeChoose(DislikeBase):
    created_at: datetime


class Dislike(DislikeBase):
    dislike_item_id: int
    dislike_user_id: int
    dislike_user: list["IUser"] = []
    dislike_item: list["Item"] = []

    class Config:
        orm_mode = True


from user.schemas import IUser
from item.schemas import Item

Like.update_forward_refs()
Dislike.update_forward_refs()
