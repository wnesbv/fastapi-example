
from fastapi import responses, Request, Depends, HTTPException, status

from sqlalchemy.orm import Session

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
            detail="no authorization, log in..!"
        )
    token = request.cookies.get("access_token")
    return token



def get_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
):

    email = auth.decode_token(token)
    print("email", email)
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user:
        raise HTTPException(401, "User doesn't exist")
    return user


def get_active_user(
    current_user: schemas.User = Depends(get_user)
):

    if not current_user.email_verified:
        raise HTTPException(401, "Электронная почта не подтверждена!")
    if not current_user.is_active:
        raise HTTPException(401, "Этот аккаунт не активен!")
    return current_user


# ...


def update_user(
    id: int,
    user_details: schemas.UserUpdate,
    db: Session,
    current_user: str,
    password: str,
):

    existing_user = db.query(
        models.User
    ).filter(models.User.id == current_user.id)

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
