import os
from datetime import datetime
from pathlib import Path, PurePosixPath

from sqlalchemy import update as sql_update
from sqlalchemy import func, and_, or_, not_, true, false
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)

from models import models
from item import schemas
from user import views


async def all_total(session, model):
    stmt = await session.execute(select(func.count(model.id)))
    result = stmt.scalars().all()
    return result


async def create_not_img_item(
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemBase,
    session: AsyncSession,
):

    new = models.Item(
        **obj_in.model_dump(),
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    session.add(new)
    await session.commit()

    return new


async def create_new_item(
    image_url: UploadFile,
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemCreate,
    session: AsyncSession,
):

    new = models.Item(
        **obj_in.model_dump(exclude={"image_url"}),
        image_url=image_url,
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    session.add(new)
    await session.commit()

    return new


# ...API create


async def api_not_img_item(
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemBase,
    session: AsyncSession,
):

    new = models.Item(
        **obj_in.model_dump(),
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    session.add(new)
    await session.commit()

    return new


async def api_new_item(
    image_url: UploadFile,
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemCreate,
    session: AsyncSession,
):

    img = obj_in.model_dump()
    del img["image_url"]
    new = models.Item(
        **img,
        image_url=image_url,
        owner_item_id=owner_item_id,
        created_at=created_at
    )

    session.add(new)
    await session.commit()

    return new


# ...img_del


async def img_del(
    id: int,
    modified_at: datetime,
    obj_in: schemas.ImgDel,
    session: AsyncSession,
):
    obj_in.__dict__.update(
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(image_url="",modified_at=modified_at)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


# ...update


async def update_item(
    id: int,
    modified_at: datetime,
    obj_in: schemas.ItemBase,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


async def img_update_item(
    id: int,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemCreate,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        image_url=image_url,
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


# ...api update


async def api_str_item(
    id: int,
    title: str,
    description: str,
    modified_at: datetime,
    obj_in: schemas.ItemUpdate,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        title=title,
        description=description,
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


async def api_update_item(
    id: int,
    title: str,
    description: str,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemUpdate,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        title=title,
        description=description,
        image_url=image_url,
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


async def api_img_item(
    id: int,
    title: str,
    description: str,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemCreate,
    session: AsyncSession,
):

    obj_in.__dict__.update(
        title=title,
        description=description,
        image_url=image_url,
        modified_at=modified_at,
    )
    query = (
        sql_update(models.Item)
        .where(models.Item.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


# ...delete

async def item_owner(
    id: int,
    user: int,
    session: AsyncSession,
):

    stmt = await session.execute(
        select(models.Item).where(
            and_(
                models.Item.id == id,
                models.Item.owner_item_id == user,
            )
        )
    )
    result = stmt.scalars().first()

    return result


async def item_delete(
    id: int,
    user: int,
    session: AsyncSession,
):

    stmt = await session.execute(
        select(models.Item).where(
            and_(
                models.Item.id == id,
                models.Item.owner_item_id == user,
            )
        )
    )
    result = stmt.scalars().first()

    await session.delete(result)
    await session.commit()

    return True


# ...list


async def retreive_item(
    id: int,
    session: AsyncSession
):

    stmt = await session.execute(
        select(models.Item).where(models.Item.id == id)
    )
    result = stmt.scalars().first()

    return result


# ...img UploadFile


async def img_creat(
    category: str,
    image_url: UploadFile,
):

    save_path = f"./static/{category}"
    file_path = f"{save_path}/{image_url.filename}"

    ext = PurePosixPath(image_url.filename).suffix
    if ext not in (".png", ".jpg", ".jpeg"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format files: png, jpg, jpeg ..!",
        )
    if Path(file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error..! File exists..!"
        )

    os.makedirs(save_path, exist_ok=True)

    with open(f"{file_path}", "wb") as fle:
        fle.write(image_url.file.read())

    return file_path.replace(".", "", 1)


# ...


async def search_item(query: str, session: AsyncSession):

    stmt =  await session.execute(
        select(models.Item).where(models.Item.title.contains(query))
    )
    obj_list = stmt.scalars().all()

    return obj_list
