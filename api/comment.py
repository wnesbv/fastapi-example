from typing import Annotated

from fastapi import APIRouter, Depends

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import models
from comment import schemas

from config.dependency import get_session
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Сomment"])


@router.get("/comment/{id}", response_model=schemas.Comment)
async def user_relationship(
    id: int,
    session: AsyncSession = Depends(get_session),
):

    stmt = await session.execute(
        select(models.User)
        .join(models.Comment.cmt_user)
        .where(models.Comment.id == id)
    )
    obj_us = stmt.scalars().unique()
    print("obj_us..", obj_us)
    stmt = await session.execute(
        select(models.Item)
        .join(models.Comment.cmt_item)
        .where(models.Comment.id == id)
    )
    obj_tm = stmt.scalars().unique()
    print("obj_tm..", obj_tm)
    stmt = await session.scalars(
        select(models.Comment).where(models.Comment.id == id)
    )
    i = stmt.scalars().first()
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
async def get_user_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
):

    stmt = await session.execute(
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
