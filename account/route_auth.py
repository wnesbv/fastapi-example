
from datetime import datetime
from typing import Annotated
from fastapi import (
    BackgroundTasks,
    APIRouter,
    Depends,
    Request,
    responses,
    Form,
    status,
)
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from user import schemas as user_schemas
from config.dependency import get_session
from user.views import get_active_user

from models import models
from .auth import auth
from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr = Form(...),
    password: str = Form(...),
    created_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):
    obj_in = user_schemas.UserCreate(email=email, created_at=created_at)
    user = await views.create_user(
        request,
        obj_in,
        auth.hash_password(password),
        background_tasks,
        session,
    )
    return responses.RedirectResponse(
        f"/user-detail/{user.id}", status_code=status.HTTP_302_FOUND
    )


# ...
@router.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    obj_in = schemas.LoginDetails(email=email, password=password)
    response = responses.RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response.token = await views.login_user(
        request, response, background_tasks, obj_in, session
    )
    return response


@router.get("/verify-email")
async def confirmation_email(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session),
):
    response = await views.account_verify_email(token, session)
    msg = "Электронная почта успешно подтверждена"
    response = templates.TemplateResponse(
        "base.html", {"request": request, "msg": msg}
    )
    return response


# ...
@router.get("/email-verify-resend")
def get_verification_email(
    request: Request,
):
    return templates.TemplateResponse(
        "auth/resend_verification_email.html",
        {"request": request},
    )


@router.post("/email-verify-resend")
async def resend_verification_email(
    requests: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    response = await views.resend_verification_email(
        requests, background_tasks, email, session
    )
    return response


# ...
@router.get("/reset-password")
def get_reset_password(
    request: Request,
):
    return templates.TemplateResponse(
        "auth/reset-password.html",
        {"request": request},
    )


@router.post("/reset-password")
async def post_reset_password(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    user = await views.get_user_by_email(email, session)
    if user:
        await views.reset_password(
            request, background_tasks, email
        )
        return templates.TemplateResponse(
            "components/successful.html",
            {
                "request": request,
                "message": "reset email sent..!",
            },
        )
    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "we don't have: email..!",
        },
    )


# ...
@router.get("/reset-password-confirm")
def get_reset_password_confirm(
    request: Request,
):
    return templates.TemplateResponse(
        "auth/reset-password-confirm.html",
        {"request": request},
    )


@router.post("/reset-password-confirm")
async def reset_password_confirm(
    request: Request,
    token: str,
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    obj_in = schemas.ResetPasswordDetails(password=password)

    email = await auth.verify_reset_token(token)
    user = await views.get_user_by_email(email, session)

    if user:
        
        pswd = auth.hash_password(password)

        obj_in.__dict__.update(password=pswd)

        query = (
            sql_update(models.User)
            .where(models.User.email == email)
            .values(obj_in.model_dump())
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(query)
        await session.commit()

        return templates.TemplateResponse(
            "components/successful.html",
            {
                "request": request,
                "message": "password reset successful..!",
            },
        )
    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "An error has occurred..!",
        },
    )


# ...
@router.get("/me")
def get_user_profile(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "current_user": current_user}
    )
