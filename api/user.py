
from typing import Annotated

from fastapi import APIRouter, Depends

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import models
from user import schemas
from item import schemas as tm_schemas

from config.dependency import get_session
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["User"])


@router.get("/current-user", response_model=schemas.GetUser)
def get_user_profile(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
):
    return current_user


@router.get("/user-relationship", response_model=schemas.IUser)
async def user_relationship(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
):
    stmt = await session.execute(
        select(models.Item.id)
        .where(models.Item.owner_item_id == current_user.id)
    )
    obj_tm = stmt.scalars().all()
    print("obj_tm..", obj_tm)

    stmt = await session.execute(
        select(models.Comment.id)
        .where(models.Comment.cmt_user_id == current_user.id)
    )
    obj_cm = stmt.scalars().all()
    print("obj_cm..", obj_cm)

    stmt = await session.execute(
        select(models.Like.upvote)
        .where(models.Like.like_user_id == current_user.id)
    )
    obj_l = stmt.scalars().all()
    print("obj_l..", obj_l)

    stmt = await session.execute(
        select(models.Dislike.downvote)
        .where(models.Dislike.dislike_user_id == current_user.id)
    )
    obj_dl = stmt.scalars().all()
    print("obj_dl..", obj_dl)

    stmt = await session.execute(
        select(models.Item)
        .where(models.Item.owner_item_id == current_user.id)
    )
    tm_all = stmt.scalars().all()

    for_item = [schemas.InItem.parse_obj(user) for user in tm_all]

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
        in_user=for_item
    )

    return obj
