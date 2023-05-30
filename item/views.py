import os
from datetime import datetime

from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Request,
    responses,
    Form,
    File,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session
from pathlib import Path, PurePosixPath

from models import models
from item import schemas


async def create_new_item(
    obj_in: schemas.ItemCreate,
    db: Session,
    image_url: UploadFile,
    owner_item_id: int,
):

    details_dict = obj_in.dict()
    del details_dict["image_url"]

    new = models.Item(
        **details_dict,
        image_url=image_url,
        owner_item_id=owner_item_id,
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


async def update_item(
    id: int,
    obj_in: schemas.ItemUpdate,
    db: Session,
    image_url: str,
    modified_at: datetime,
):
    existing_item = db.query(
        models.Item
    ).filter(models.Item.id == id)

    obj_in.__dict__.update(
        image_url=image_url,
        modified_at=modified_at,
    )
    existing_item.update(obj_in.__dict__)
    db.commit()

    return existing_item


async def item_delete(
    id: int,
    db: Session,
):
    db.query(
        models.Item
    ).filter(models.Item.id == id).delete()
    db.commit()

    return True


# ...


def list_item(db: Session):

    obj_list = db.query(models.Item).all()

    return obj_list


def list_user_item(
    db: Session,
    owner_item_id,
):
    obj_list = db.query(
        models.Item
    ).filter(models.Item.owner_item_id == owner_item_id)

    return obj_list


def retreive_item(
    id: int,
    db: Session
):

    obj = db.query(
        models.Item
    ).filter(models.Item.id == id).first()

    return obj


# ...


async def img_creat(
    category: str = Form(...),
    image_url: UploadFile = File(...)
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
            status_code=status.HTTP_400_BAD_REQUEST, detail="Error..! File exists..!"
        )
    os.makedirs(save_path, exist_ok=True)

    with open(f"{file_path}", "wb") as fle:
        fle.write(image_url.file.read())
        
    return file_path.replace(".", "", 1)


# ...


def search_item(query: str, db: Session):

    obj_list = db.query(
        models.Item
    ).filter(models.Item.title.contains(query))

    return obj_list
