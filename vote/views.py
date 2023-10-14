
from sqlalchemy import func, and_, or_, not_, true, false
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import models
from vote import schemas


async def like_add(
    like_item_id: int,
    like_user_id: int,
    obj_in: schemas.LikeChoose,
    session: AsyncSession,
):

    new = models.Like(
        **obj_in.model_dump(),
        like_user_id=like_user_id,
        like_item_id=like_item_id,
    )
    session.add(new)
    await session.commit()

    return new


# ...


async def dislike_add(
    dislike_item_id: int,
    dislike_user_id: int,
    obj_in: schemas.Dislike,
    session: AsyncSession,
):

    new = models.Dislike(
        **obj_in.model_dump(),
        dislike_user_id=dislike_user_id,
        dislike_item_id=dislike_item_id,
    )
    session.add(new)
    await session.commit()

    return new


# ...

async def retreive_like(
    id: int,
    current_user: int,
    session: AsyncSession,
):

    stmt = await session.execute(
        select(models.Like).where(
            and_(
                models.Like.like_item_id == id,
                models.Like.like_user_id == current_user
            )
        )
    )
    result = stmt.scalars().first()

    return result


async def retreive_dislike(
    id: int,
    current_user: int,
    session: AsyncSession,
):

    stmt = await session.execute(
        select(models.Dislike).where(
            and_(
                models.Dislike.dislike_item_id == id,
                models.Dislike.dislike_user_id == current_user
            )
        )
    )
    result = stmt.scalars().first()

    return result
