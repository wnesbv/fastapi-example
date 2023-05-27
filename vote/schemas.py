
from pydantic import BaseModel


class LikeBase(BaseModel):
    upvote: bool


class LikeChoose(LikeBase):
    like_item_id: int


class Like(LikeBase):
    like_item_id: int
    like_user_id: int
    like_user: list["User"] = []
    like_item: list["Item"] = []

    class Config:
        orm_mode = True


# ...


class DislikeBase(BaseModel):
    downvote: bool


class DislikeChoose(DislikeBase):
    dislike_item_id: int


class Dislike(DislikeBase):
    dislike_item_id: int
    dislike_user_id: int
    dislike_user: list["User"] = []
    dislike_item: list["Item"] = []

    class Config:
        orm_mode = True


from user.schemas import User
from item.schemas import Item

Like.update_forward_refs()
Dislike.update_forward_refs()