

from sqlalchemy.orm import Session

from models import models
from vote import schemas


async def like_add(
    like_in: schemas.LikeChoose,
    db: Session,
    like_user_id: int,
    like_item_id: int,
):

    new = models.Like(
        **like_in.dict(),
        like_user_id=like_user_id,
        like_item_id=like_item_id,
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new


# ...


async def dislike_add(
    dislike_in: schemas.Dislike,
    db: Session,
    dislike_item_id: int,
    dislike_user_id: int,
):

    new = models.Dislike(
        **dislike_in.dict(),
        dislike_user_id=dislike_user_id,
        dislike_item_id=dislike_item_id,
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new


# ...

def retreive_like(
    id: int,
    db: Session,
    current_user,
):

    obj = db.query(models.Like).filter(
        models.Like.like_item_id == id,
        models.Like.like_user_id == current_user
    ).first()

    return obj


def retreive_dislike(
    id: int,
    db: Session,
    current_user,
):

    obj = db.query(models.Dislike).filter(
        models.Dislike.dislike_item_id == id,
        models.Dislike.dislike_user_id == current_user
    ).first()

    return obj
