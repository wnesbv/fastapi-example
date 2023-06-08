from typing import Annotated

from fastapi import APIRouter, Depends

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from user import schemas

from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["User"])


@router.get("/current-user", response_model=schemas.GetUser)
def get_user_profile(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
):
    return current_user


@router.get("/user-relationship", response_model=schemas.IUser)
def user_relationship(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    obj_tm = (
        db.execute(
            select(
                models.Item.id,
                models.Item.title,
                models.Item.description,
                models.Item.owner_item_id,
            )
            .join(models.User.user_item)
            .where(models.Item.owner_item_id == current_user.id)
        )
        .unique()
        .all()
    )
    print("obj_tm..", obj_tm)
    obj_cm = (
        db.execute(
            select(
                models.Comment.id,
                models.Comment.opinion_expressed,
                models.Comment.cmt_user_id,
                models.Comment.cmt_item_id,
            )
            .join(models.User.user_cmt)
            .where(models.Comment.cmt_user_id == current_user.id)
        )
        .unique()
        .all()
    )
    print("obj_cm..", obj_cm)
    obj_l = (
        db.execute(
            select(
                models.Like.upvote, models.Like.like_user_id, models.Like.like_item_id
            )
            .join(models.User.user_like)
            .where(models.Like.like_user_id == current_user.id)
        )
        .unique()
        .all()
    )
    print("obj_l..", obj_l)
    obj_dl = (
        db.execute(
            select(
                models.Dislike.downvote,
                models.Dislike.dislike_user_id,
                models.Dislike.dislike_item_id,
            )
            .join(models.User.user_dislike)
            .where(models.Dislike.dislike_user_id == current_user.id)
        )
        .unique()
        .all()
    )
    print("obj_dl..", obj_dl)

    obj = schemas.IUser(
        id=current_user.id,
        email=current_user.email,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        user_item=obj_tm,
        user_cmt=obj_cm,
        user_like=obj_l,
        user_dislike=obj_dl,
    )

    return obj
