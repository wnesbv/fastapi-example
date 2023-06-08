from typing import Annotated

from fastapi import APIRouter, Depends

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from comment import schemas

from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Сomment"])


@router.get("/comment/{id}", response_model=schemas.Comment)
def user_relationship(
    id: int,
    db: Session = Depends(get_db),
):

    obj_us = (
        db.execute(
            select(
                models.User.id,
                models.User.email,
                models.User.email_verified,
                models.User.is_active,
                models.User.is_admin,
            )
            .join(models.Comment.cmt_user)
        )
        .unique()
        .all()
    )
    print("obj_us..", obj_us)

    obj_tm = (
        db.execute(
            select(
                models.Item.id,
                models.Item.title,
                models.Item.description,
                models.Item.owner_item_id,
            )
            .join(models.Comment.cmt_item)
        )
        .unique()
        .all()
    )
    print("obj_tm..", obj_tm)


    i = db.scalars(
        select(models.Comment).where(models.Comment.id == id)
    ).first()

    obj = schemas.Comment(
        id=i.id,
        opinion_expressed=i.opinion_expressed,
        created_at=i.created_at,
        modified_at=i.modified_at,
        cmt_user_id=i.cmt_user_id,
        cmt_item_id=i.cmt_item_id,
        cmt_user=obj_us,
        cmt_item=obj_tm,
    )

    return obj


@router.get("/user-comment", response_model=list[schemas.CmtUser])
def get_user_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    stmt = db.execute(
        select(models.Comment)
        .where(models.Comment.cmt_user_id == current_user.id)
    )
    result = stmt.scalars().all()

    obj = [
        schemas.CmtUser(
            id=i.id,
            opinion_expressed=i.opinion_expressed,
            created_at=i.created_at,
            modified_at=i.modified_at,
            cmt_user_id=i.cmt_user_id,
            cmt_item_id=i.cmt_item_id,
        )
        for i in result
    ]
    return obj
