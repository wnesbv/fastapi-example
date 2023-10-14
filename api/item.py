from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile,
)

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import models
from item import schemas, views

from config.dependency import get_session
from user.views import get_active_user
from options_select.opt import in_all, left_right_first, left_right_all


router = APIRouter(prefix="/docs", tags=["Item"])


@router.post("/create-item")
async def create_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    session: AsyncSession = Depends(get_session),
):
    exists = await left_right_first(session, models.Item, models.Item.title, title)

    if exists:
        return {"msg": "such a title already exists..!"}

    if not image_url or not category:

        obj_in = schemas.ItemBase(title=title, description=description)

        await views.api_not_img_item(current_user.id, datetime.now(), obj_in, session)

        return obj_in

    obj_in = schemas.ItemCreate(
        title=title, description=description, image_url=image_url
    )
    upload = await views.img_creat(category, image_url)

    await views.api_new_item(upload, current_user.id, datetime.now(), obj_in, session)

    return obj_in


# ...update


@router.get("/update-item/{id}", response_model=schemas.ListItem)
async def get_update(
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
):
    i = await left_right_first(session, models.Item, models.Item.id, id)

    if i.owner_item_id == current_user.id:
        obj_in = schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )

        return obj_in

    return {"msg": "You are not permitted..!"}


@router.patch("/update-item/{id}")
async def update(
    id: int,
    title: str = Form(""),
    description: str = Form(""),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    delete_bool: bool = Form(False),
    modified_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):
    i = await left_right_first(session, models.Item, models.Item.id, id)

    if not title:
        if not description:
            if not image_url and not category:
                obj_in = schemas.ItemBase(
                    title=title,
                    description=description,
                )
                await views.api_update_item(
                    id,
                    i.title,
                    i.description,
                    i.image_url,
                    datetime.now(),
                    obj_in,
                    session,
                )

                if delete_bool is True:
                    if Path(f".{i.image_url}").exists():
                        Path.unlink(f".{i.image_url}")

                    img_not = schemas.ImgDel(
                        image_url=image_url,
                        modified_at=datetime.now(),
                    )
                    await views.img_del(id, modified_at, img_not, session)
                    return img_not

                return obj_in

            obj_in = schemas.ItemCreate(
                title=title,
                description=description,
                image_url=image_url,
            )
            upload = await views.img_creat(category, image_url)
            await views.api_img_item(
                id,
                i.title,
                i.description,
                upload,
                datetime.now(),
                obj_in,
                session,
            )
            return obj_in

        obj_in = schemas.ItemUpdate(
            title=title,
            description=description,
            image_url=image_url,
        )
        await views.api_update_item(
            id,
            i.title,
            description,
            i.image_url,
            datetime.now(),
            obj_in,
            session,
        )
        return obj_in

    obj_in = schemas.ItemUpdate(
        title=title,
        description=description,
        image_url=image_url,
    )
    await views.api_update_item(
        id,
        title,
        i.description,
        i.image_url,
        datetime.now(),
        obj_in,
        session,
    )
    return obj_in


# ...list


@router.get("/item-list", response_model=list[schemas.ListItem])
async def item_list(
    session: AsyncSession = Depends(get_session),
):
    obj_list = await in_all(session, models.Item)

    obj_in = [
        schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )
        for i in obj_list
    ]
    return obj_in


@router.get("/item-id/{id}", response_model=schemas.Item)
async def item_id(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = await session.execute(select(models.Item.id).where(models.Item.id == id))
    obj_tm = stmt.scalars().all()
    print("obj_tm..", obj_tm)

    stmt = await session.execute(
        select(models.Comment.id).where(models.Comment.cmt_item_id == id)
    )
    obj_cm = stmt.scalars().all()
    print("obj_cm..", obj_cm)

    stmt = await session.execute(
        select(models.Like.upvote).where(models.Like.like_item_id == id)
    )
    obj_l = stmt.scalars().all()
    print("obj_l..", obj_l)

    stmt = await session.execute(
        select(models.Dislike.downvote).where(models.Dislike.dislike_item_id == id)
    )
    obj_dl = stmt.scalars().all()
    print("obj_dl..", obj_dl)

    i = await left_right_first(session, models.Item, models.Item.id, id)

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
async def get_user_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
):

    result = await left_right_all(session, models.Item, models.Item.owner_item_id, current_user.id)

    obj_in = [
        schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )
        for i in result
    ]
    return obj_in
