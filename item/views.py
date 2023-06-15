import os
from datetime import datetime

from pathlib import Path, PurePosixPath

from fastapi import (
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from item import schemas


async def create_not_img_item(
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemBase,
    db: Session,
):

    new = models.Item(
        **obj_in.dict(),
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


async def create_new_item(
    image_url: UploadFile,
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemCreate,
    db: Session,
):

    new = models.Item(
        **obj_in.dict(),
        image_url=image_url,
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


# ...API create


async def api_not_img_item(
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemBase,
        db: Session,
):

    new = models.Item(
        **obj_in.dict(),
        owner_item_id=owner_item_id,
        created_at=created_at,
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


async def api_new_item(
    image_url: UploadFile,
    owner_item_id: int,
    created_at: datetime,
    obj_in: schemas.ItemCreate,
    db: Session,
):

    img = obj_in.dict()
    del img["image_url"]
    new = models.Item(
        **img,
        image_url=image_url,
        owner_item_id=owner_item_id,
        created_at=created_at
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


# ...img_del


async def img_del(
    id: int,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ImgDel,
    db: Session,
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


# ...update


async def update_item(
    id: int,
    modified_at: datetime,
    obj_in: schemas.ItemBase,
    db: Session,
):

    existing_item = db.query(
        models.Item
    ).filter(models.Item.id == id)

    obj_in.__dict__.update(
        modified_at=modified_at,
    )
    existing_item.update(obj_in.__dict__)
    db.commit()

    return existing_item


async def img_update_item(
    id: int,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemCreate,
    db: Session,
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


# ...api update


async def api_str_item(
    id: int,
    title: str,
    description: str,
    modified_at: datetime,
    obj_in: schemas.ItemUpdate,
    db: Session,
):
    existing_item = db.query(
        models.Item
    ).filter(models.Item.id == id)

    obj_in.__dict__.update(
        title=title,
        description=description,
        modified_at=modified_at,
    )
    existing_item.update(obj_in.__dict__)
    db.commit()

    return existing_item


async def api_update_item(
    id: int,
    title: str,
    description: str,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemUpdate,
    db: Session,
):
    existing_item = db.query(
        models.Item
    ).filter(models.Item.id == id)

    obj_in.__dict__.update(
        title=title,
        description=description,
        image_url=image_url,
        modified_at=modified_at,
    )
    existing_item.update(obj_in.__dict__)
    db.commit()

    return existing_item


async def api_img_item(
    id: int,
    title: str,
    description: str,
    image_url: str,
    modified_at: datetime,
    obj_in: schemas.ItemCreate,
    db: Session,
):
    existing_item = db.query(
        models.Item
    ).filter(models.Item.id == id)

    obj_in.__dict__.update(
        title=title,
        description=description,
        image_url=image_url,
        modified_at=modified_at,
    )
    existing_item.update(obj_in.__dict__)
    db.commit()

    return existing_item


# ...delete


async def item_delete(
    id: int,
    db: Session,
):
    db.query(
        models.Item
    ).filter(models.Item.id == id).delete()
    db.commit()

    return True


# ...list


async def retreive_item(
    id: int,
    db: Session
):

    stmt = db.execute(
        select(models.Item).where(models.Item.id == id)
    )
    result = stmt.scalars().first()

    return result


def list_item(db: Session):

    obj_list = db.execute(select(models.Item)).scalars().all()

    return obj_list


def list_user_item(
    owner_item_id: int,
    db: Session,
):

    stmt = db.execute(
        select(models.Item)
        .where(models.Item.owner_item_id == owner_item_id)
    )
    result = stmt.scalars().all()


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


def search_item(query: str, db: Session):

    obj_list = db.query(
        models.Item
    ).filter(models.Item.title.contains(query))

    return obj_list
