
import random, shutil

from sqlalchemy import func, and_, or_, not_, true, false
from sqlalchemy.future import select


async def all_total(session, model):
    stmt = await session.execute(select(func.count(model.id)))
    result = stmt.scalars().all()
    return result


async def in_all(session, model):
    stmt = await session.execute(select(model))
    result = stmt.scalars().all()
    return result


async def left_right_first(session, model, left, right):
    stmt = await session.execute(
        select(model)
        .where(left == right)
    )
    result = stmt.scalars().first()
    return result

async def left_right_all(session, model, left, right):
    stmt = await session.execute(
        select(model)
        .where(left == right)
    )
    result = stmt.scalars().all()
    return result


async def id_and_owner(session, model, obj, id):
    stmt = await session.execute(
        select(model).where(
            and_(
                model.id == id,
                model.owner == obj,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def owner_request(session, model, obj):
    stmt = await session.execute(
        select(model).where(model.owner == obj)
    )
    result = stmt.scalars().all()
    return result
