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
