from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from item import views, schemas

from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Item"])


@router.get("/item-list", response_model=list[schemas.ListItem])
def item_list(
    db: Session = Depends(get_db),
):

    obj_list = db.execute(select(models.Item)).scalars().all()

    obj = [
        schemas.ListItem(
            id=t.id,
            title=t.title,
            description=t.description,
            image_url=t.image_url,
            created_at=t.created_at,
            modified_at=t.modified_at,
            owner_item_id=t.owner_item_id,
        )
        for t in obj_list
    ]
    return obj


@router.get("/item-id/{id}", response_model=schemas.Item)
def item_id(
    id: int,
    db: Session = Depends(get_db),
):
    obj_tm = (
        db.execute(
            select(
                models.User.id,
                models.User.email,
                models.User.email_verified,
                models.User.is_active,
                models.User.is_admin,
            )
            .join(models.Item.item_user)
            .where(models.Item.owner_item_id == id)
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
            .join(models.Item.item_cmt)
            .where(models.Comment.cmt_item_id == id)
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
            .join(models.Item.item_like)
            .where(models.Like.like_item_id == id)
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
            .join(models.Item.item_dislike)
            .where(models.Dislike.dislike_item_id == id)
        )
        .unique()
        .all()
    )
    print("obj_dl..", obj_dl)

    i = db.scalars(
        select(models.Item).where(models.Item.id == id)
    ).first()

    obj = schemas.Item(
        id=i.id,
        title=i.title,
        description=i.description,
        image_url=i.image_url,
        created_at=i.created_at,
        modified_at=i.modified_at,
        owner_item_id=i.owner_item_id,
        item_user=obj_tm,
        item_cmt=obj_cm,
        item_like=obj_l,
        item_dislike=obj_dl,
    )

    return obj


@router.get("/user-item", response_model=list[schemas.ListItem])
def get_user_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    stmt = db.execute(
        select(models.Item)
        .where(models.Item.owner_item_id == current_user.id)
    )
    result = stmt.scalars().all()

    obj = [
        schemas.ListItem(
            id=t.id,
            title=t.title,
            description=t.description,
            image_url=t.image_url,
            created_at=t.created_at,
            modified_at=t.modified_at,
            owner_item_id=t.owner_item_id,
        )
        for t in result
    ]
    return obj
