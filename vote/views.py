

from sqlalchemy.orm import Session

from models import models
from vote import schemas


def like_add(
    like_in: schemas.Like,
    db: Session,
    like_user_id: int,
):

    new_like = models.Like(
        **like_in.dict(),
        like_user_id=like_user_id,
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like


# ...

def dislike_add(
    dislike_in: schemas.Dislike,
    db: Session,
    dislike_user_id: int,
):

    new_dislike = models.Dislike(
        **dislike_in.dict(),
        dislike_user_id=dislike_user_id,
    )
    db.add(new_dislike)
    db.commit()
    db.refresh(new_dislike)

    return new_dislike


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
