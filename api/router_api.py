from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Request,
    Response,
    HTTPException,
)

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from account import schemas, views
from user import schemas as user_schemas

from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Authentication"])


@router.post("/register", response_model=user_schemas.UserCreate)
def register_user(
    request: Request,
    background_tasks: BackgroundTasks,
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db),
):
    user = views.create_user(user, db, background_tasks, request)

    return user


@router.post("/login", response_model=schemas.Token)
def login(
    *,
    user_details: schemas.LoginDetails,
    db: Session = Depends(get_db),
    bg_tasks: BackgroundTasks,
    request: Request,
    response: Response,
):
    token = views.login_user(user_details, db, bg_tasks, request, response)

    return token


@router.get("/email-verify")
def api_verify_email(token: str, db: Session = Depends(get_db)):
    response = views.verify_email(token, db)

    return response


@router.get("/email-verify-resend")
def resend_verification_email(
    email: EmailStr,
    background_tasks: BackgroundTasks,
    requests: Request,
    db: Session = Depends(get_db),
):
    response = views.resend_verification_email(email, background_tasks, requests, db)
    return response


# ..


@router.get("/reset-password")
def reset_password(
    email: EmailStr,
    bg_tasks: BackgroundTasks,
    requests: Request,
    db: Session = Depends(get_db),
):
    done = views.reset_password(email, bg_tasks, requests, db)
    if not done:
        raise HTTPException(500, "При обработке вашего запроса произошла ошибка..!")
    return {"msg": "Reset email sent"}


# ..


@router.post("/reset-password-confirm")
def rest_password_confirm(
    body: schemas.ResetPasswordDetails,
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    done = views.reset_password_verification(body, request, bg_tasks, db)
    if not done:
        raise HTTPException(500, "An error has occurred..!")
    return {"msg": "Password reset successful"}


# ...


@router.get("/current-user", response_model=user_schemas.GetUser)
def get_user_profile(
    # current_user: user_schemas.User = Depends(get_active_user)
    current_user: Annotated[EmailStr, Depends(get_active_user)],
):
    return current_user


@router.get("/user-relationship", response_model=user_schemas.User)
def user_relationship(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    obj_tm = (
        db.execute(
            select(
                models.Item.id, models.Item.title, models.Item.description, models.Item.owner_item_id
            )
            .join(models.User.user_item)
            .where(models.Item.owner_item_id == current_user.id)
        )
        .unique()
        .all()
    )
    obj_cm = (
        db.execute(
            select(
                models.Comment.id, models.Comment.opinion_expressed, models.Comment.cmt_user_id, models.Comment.cmt_item_id
            )
            .join(models.User.user_cmt)
            .where(models.Comment.cmt_user_id == current_user.id)
        )
        .unique()
        .all()
    )
    obj_l = (
        db.execute(
            select(
                models.Like.upvote, models.Like.like_user_id, models.Like.like_item_id
            )
            .join(models.User.user_like)
            .where(models.Like.like_user_id == current_user.id)
        )
        .unique()
        .all()
    )
    obj_dl = (
        db.execute(
            select(
                models.Dislike.downvote, models.Dislike.dislike_user_id,  models.Dislike.dislike_item_id, 
            )
            .join(models.User.user_dislike)
            .where(models.Dislike.dislike_user_id == current_user.id)
        )
        .unique()
        .all()
    )

    obj = user_schemas.User(
        id=current_user.id,
        email=current_user.email,
        password=current_user.password,
        email_verified=current_user.email_verified,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        user_item=obj_tm,
        user_cmt=obj_cm,
        user_like=obj_l,
        user_dislike=obj_dl,
    )

    return obj
