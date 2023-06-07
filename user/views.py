
import jwt
from fastapi import Request, Depends, HTTPException, status

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy.future import select

from user import schemas
from models import models

from account.auth import auth
from config.dependency import get_db


def get_token(
    request: Request,
):
    if not request.cookies.get("access_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no authorization, log in..!",
        )
    token = request.cookies.get("access_token")
    return token


def get_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
):

    email = auth.decode_token(token)
    print("email", email)

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(401, "User doesn't exist")
    return user


def get_active_user(
    current_user: schemas.GetUser = Depends(get_user)
):

    if not current_user.email_verified:
        raise HTTPException(401, "Электронная почта не подтверждена!")
    if not current_user.is_active:
        raise HTTPException(401, "Этот аккаунт не активен!")
    return current_user


# ...


async def update_user(
    id: int,
    current_user: str,
    password: str,
    db: Session,
    user_details: schemas.UserUpdate,
):

    existing_user = db.query(models.User).filter(models.User.id == current_user.id)

    user_details.__dict__.update(password=password)
    existing_user.update(user_details.__dict__)
    db.commit()

    return existing_user


# ...


def list_user(db: Session):

    obj_list = db.query(models.User).all()

    return obj_list


def retreive_user(id: int, db: Session):

    obj = db.query(models.User).filter(models.User.id == id).first()

    return obj


def count_user_item(id: int, db: Session):
    obj = (
        db.execute(
            select(models.Item.id)
            .join(models.User.user_item)
            .where(models.Item.owner_item_id == id)
        )
        .unique()
        .all()
    )

    return obj
