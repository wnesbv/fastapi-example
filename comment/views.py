
from datetime import datetime

from sqlalchemy.orm import Session

from models import models
from . import schemas


async def comment_create(
    obj_in: schemas.CmtCreate,
    db: Session,
    cmt_user_id: int,
    cmt_item_id: int,
):

    new = models.Comment(
        **obj_in.dict(),
        cmt_user_id=cmt_user_id,
        cmt_item_id=cmt_item_id,
    )

    db.add(new)
    db.commit()
    db.refresh(new)

    return new


async def up_comment(
    id: int,
    cmt: schemas.CmtUpdate,
    db: Session,
    modified_at: datetime,
):
    existing_cmt = db.query(
        models.Comment
    ).filter(models.Comment.id == id)

    cmt.__dict__.update(
        modified_at=modified_at
    )
    existing_cmt.update(cmt.__dict__)
    db.commit()

    return existing_cmt


async def comment_delete(
    id: int,
    db: Session,
):

    existing_cmt = db.query(
        models.Comment
    ).filter(models.Comment.id == id)

    if not existing_cmt.first():
        return False

    existing_cmt.delete(synchronize_session=False)
    db.commit()

    return existing_cmt


# ...


def retreive_cmt(
    id: int,
    db: Session
):

    obj = db.query(
        models.Comment
    ).filter(models.Comment.id == id).first()

    return obj


def list_cmt(db: Session):

    obj_list = db.query(models.Comment).all()

    return obj_list
