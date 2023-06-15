from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    File,
    UploadFile,
    status,
    responses,
)

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from item import schemas, views

from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Item"])


@router.post("/create-item")
async def create_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    exists = db.query(models.Item).filter(models.Item.title == title).first()

    if exists:
        return {"msg": "such a title already exists..!"}

    if not image_url or not category:
        i = schemas.ItemBase(title=title, description=description)
        await views.api_not_img_item(
            owner_item_id=current_user.id,
            created_at=datetime.now(),
            obj_in=i,
            db=db,
        )
        return i

    img = schemas.ItemCreate(title=title, description=description, image_url=image_url)
    upload = await views.img_creat(category, image_url)

    await views.api_new_item(
        image_url=upload,
        owner_item_id=current_user.id,
        created_at=datetime.now(),
        obj_in=img,
        db=db,
    )

    return img


# ...update


@router.get("/update-item/{id}", response_model=schemas.ListItem)
async def get_update(
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    i = await views.retreive_item(id=id, db=db)

    if i.owner_item_id == current_user.id:
        obj = schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )

        return obj

    return {"msg": "You are not permitted..!"}


@router.patch("/update-item/{id}")
async def update(
    id: int,
    title: str = Form(""),
    description: str = Form(""),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    delete_bool: bool = Form(False),
    db: Session = Depends(get_db),
):

    i = await views.retreive_item(id=id, db=db)

    if not title:
        if not description:
            if not image_url and not category:
                obj_file = schemas.ItemBase(
                    title=title,
                    description=description,
                )
                await views.api_update_item(
                    id=id,
                    title=i.title,
                    description=i.description,
                    image_url=i.image_url,
                    modified_at=datetime.now(),
                    obj_in=obj_file,
                    db=db,
                )

                if delete_bool is True:

                    if Path(f".{i.image_url}").exists():
                        Path.unlink(f".{i.image_url}")

                    img_del = schemas.ImgDel(
                        image_url=image_url,
                        modified_at=datetime.now(),
                    )
                    await views.img_del(
                        id=id, image_url="",
                        modified_at=datetime.now(),
                        obj_in=img_del,
                        db=db,
                    )
                    return img_del

                return obj_file

            img = schemas.ItemCreate(
                title=title,
                description=description,
                image_url=image_url,
            )
            upload = await views.img_creat(category, image_url)
            await views.api_img_item(
                id=id,
                title=i.title,
                description=i.description,
                image_url=upload,
                modified_at=datetime.now(),
                obj_in=img,
                db=db
            )
            return img


        obj_str = schemas.ItemUpdate(
            title=title,
            description=description,
            image_url=image_url,
        )
        await views.api_update_item(
            id=id,
            title=i.title,
            description=description,
            image_url=i.image_url,
            modified_at=datetime.now(),
            obj_in=obj_str,
            db=db,
        )
        return obj_str

    obj_str = schemas.ItemUpdate(
        title=title,
        description=description,
        image_url=image_url,
    )
    await views.api_update_item(
        id=id,
        title=title,
        description=i.description,
        image_url=i.image_url,
        modified_at=datetime.now(),
        obj_in=obj_str,
        db=db,
    )
    return obj_str


# ...list


@router.get("/item-list", response_model=list[schemas.ListItem])
def item_list(
    db: Session = Depends(get_db),
):
    obj_list = db.execute(select(models.Item)).scalars().all()

    obj = [
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
            .where(models.Item.id == id)
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
            .where(models.Item.id == id)
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
            .where(models.Item.id == id)
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
            .where(models.Item.id == id)
        )
        .unique()
        .all()
    )
    print("obj_dl..", obj_dl)

    i = db.scalars(select(models.Item).where(models.Item.id == id)).first()

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
        select(models.Item).where(models.Item.owner_item_id == current_user.id)
    )
    result = stmt.scalars().all()

    obj = [
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
    return obj
