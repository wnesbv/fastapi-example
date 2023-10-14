
from datetime import datetime

from sqlalchemy import update as sql_update
from sqlalchemy import func, and_, or_, not_, true, false
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import models
from . import schemas


async def comment_create(
    cmt_user_id: int,
    cmt_item_id: int,
    obj_in: schemas.CmtCreate,
    session: AsyncSession,
):

    new = models.Comment(
        **obj_in.model_dump(),
        cmt_user_id=cmt_user_id,
        cmt_item_id=cmt_item_id,
    )

    session.add(new)
    await session.commit()

    return new


async def up_comment(
    id: int,
    modified_at: datetime,
    obj_in: schemas.CmtUpdate,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        modified_at=modified_at
    )
    query = (
        sql_update(models.Comment)
        .where(models.Comment.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


async def comment_delete(
    id: int,
    user: int,
    session: AsyncSession,
):

    stmt = await session.execute(
        select(models.Comment).where(
            and_(
                models.Comment.id == id,
                models.Comment.cmt_user_id == user,
            )
        )
    )
    result = stmt.scalars().first()

    result.delete(synchronize_session=False)
    await session.commit()

    return result
