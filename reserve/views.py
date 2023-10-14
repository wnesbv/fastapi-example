import os
from datetime import datetime

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import models, reserverent


async def period_item(
    time_start: datetime,
    time_end: datetime,
    session: AsyncSession,
):
    rsv = await session.execute(select(models.Item.id).join(reserverent.ReserveRentFor.rrf_tm))
    rsv_list = rsv.scalars().all()
    i = await session.execute(select(reserverent.ReserveRentFor.time_start))
    start = i.scalars().all()
    i = await session.execute(select(reserverent.ReserveRentFor.time_end))
    end = i.scalars().all()

    # ..
    stmt = await session.execute(
        select(models.Item)
        .join(
            reserverent.ReserveRentFor.rrf_tm,
        )
        .where(models.Item.id.in_(rsv_list))
        .where(func.datetime(time_start).not_in(start))
        .where(func.datetime(time_end).not_in(end))
    )
    result = stmt.scalars().unique().all()
    # ..
    return result


async def not_period(session: AsyncSession):
    # ..
    rsv = await session.execute(select(models.Item.id).join(reserverent.ReserveRentFor.rrf_tm))
    rsv_list = rsv.scalars().all()
    print("rsv_list..", rsv_list)
    # ..
    stmt = await session.execute(select(models.Item).where(models.Item.id.not_in(rsv_list)))
    result = stmt.scalars().unique().all()
    # ..
    return result


async def rrf_details(
    id: int,
    rrf_us_id: int,
    session: AsyncSession,
):
    stmt = await session.execute(
        select(reserverent.ReserveRentFor)
        .where(
            and_(
                reserverent.ReserveRentFor.id == id,
                reserverent.ReserveRentFor.rrf_us_id == rrf_us_id,
            )
        )
    )
    result = stmt.scalars().first()

    return result
