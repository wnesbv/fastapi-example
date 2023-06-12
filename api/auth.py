
from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Request,
    Response,
    Form,
    HTTPException,
)

from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from models import models
from account import schemas, views
from user import schemas as user_schemas
from account.auth import auth
from config.dependency import get_db
from user.views import get_active_user


router = APIRouter(prefix="/docs", tags=["Authentication"])


@router.post("/register", response_model=user_schemas.UserRegister)
def register_user(
    request: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    user = user_schemas.UserRegister(
        email=email
    )

    views.api_create_user(
        request=request,
        background_tasks=background_tasks,
        obj_in=user,
        password=auth.hash_password(password),
        created_at=datetime.now(),
        db=db,
    )
    return user


@router.post("/login", response_model=schemas.Token)
async def login(
    *,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    user_details: schemas.LoginDetails,
    db: Session = Depends(get_db),

):
    token = await views.login_user(request, response, background_tasks, user_details, db)

    return token


@router.get("/email-verify")
def api_verify_email(token: str, db: Session = Depends(get_db)):

    response = views.verify_email(token, db)

    return response


@router.post("/email-verify-resend")
async def resend_email(
    requests: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr,
    db: Session = Depends(get_db),
):

    response = await views.resend_verification_email(requests, background_tasks, email, db)

    return response


# ..


@router.post("/reset-password")
async def reset_password_email(
    requests: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr,
):

    done = await views.reset_password(requests, background_tasks, email)

    if not done:
        raise HTTPException(500, "При обработке вашего запроса произошла ошибка..!")

    return {"msg": "Reset email sent"}


# ..


@router.post("/reset-password-confirm")
async def rest_password_confirm(
    request: Request,
    background_tasks: BackgroundTasks,
    body: schemas.ResetPasswordDetails,
):

    done = await views.reset_password(request, background_tasks, body)
    if not done:
        raise HTTPException(500, "An error has occurred..!")

    return {"msg": "Password reset successful"}
