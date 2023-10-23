from datetime import datetime

from fastapi import BackgroundTasks, HTTPException, status, Request, Response

from pydantic import EmailStr

from sqlalchemy import false, and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import models

from config.settings import settings
from config.mail import send_mail
from user.schemas import UserCreate
from .auth import auth
from . import schemas


# ..
async def get_user_by_email(email, session):
    stmt = await session.execute(select(models.User).where(models.User.email == email))
    result = stmt.scalars().first()
    return result


async def get_user_by_id(id, session):
    stmt = await session.execute(select(models.User).where(models.User.id == id))
    result = stmt.scalars().first()
    return result


# ..


def generate_verification_email_link(request, email):
    email_token = auth.encode_verification_token(email)
    base_url = request.base_url
    verification_link = f"{base_url}verify-email?token={email_token}"

    return verification_link


def send_verification_email(
    request: Request,
    email: EmailStr,
    background_tasks: BackgroundTasks,
):
    verification_link = generate_verification_email_link(request, email)

    email = schemas.EmailSchema(
        email=[email],
        body={
            "verification_link": verification_link,
            "company_name": settings.PROJECT_TITLE,
        },
    )

    send_mail(
        background_tasks=background_tasks,
        subject=f"{settings.PROJECT_TITLE} email confirmation",
        email=email,
        template_name="email_verification.html",
    )


async def create_user(
    request: Request,
    obj_in: UserCreate,
    password: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
):
    old_user = await get_user_by_email(obj_in.email, session)
    if old_user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User with this email already exists"
        )
    send_verification_email(
        request,
        obj_in.email,
        background_tasks,
    )
    new = models.User(**obj_in.model_dump(), password=password)
    session.add(new)
    await session.commit()
    return new


async def api_create_user(
    request: Request,
    password: str,
    created_at: datetime,
    obj_in: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
):
    print("useremail", obj_in.email)
    user = await get_user_by_email(obj_in.email, session)

    if user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User with this email already exists"
        )

    new = models.User(**obj_in.model_dump(), password=password, created_at=created_at)
    session.add(new)
    await session.commit()

    send_verification_email(
        request,
        obj_in.email,
        background_tasks,
    )

    return new


async def login_user(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    obj_in: schemas.LoginDetails,
    session: AsyncSession,
):
    stmt = await session.execute(
        select(models.User)
        .where(
            and_(
                models.User.email == obj_in.email,
                models.User.privileged == false()
            )
        )
    )
    user = stmt.scalars().first()
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "User with this email doesn't exist!"
        )
    if not await auth.verify_password(obj_in.password, user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password!")
    if not user.email_verified:
        send_verification_email(request, obj_in.email, background_tasks)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Электронная почта не подтверждена. Проверьте свою почту, чтобы узнать, как пройти верификацию.",
        )
    # ...
    access_token = await auth.encode_token(user.email, user)

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("access_user", user.email, httponly=True)

    return schemas.Token(access_token=access_token, token_type="bearer")


# ...


async def account_verify_email(
    token: str,
    session: AsyncSession,
):
    email = auth.verify_email(token)
    user = await get_user_by_email(email, session)
    if not user:
        raise HTTPException(
            401, "Недействительный пользователь... Пожалуйста, создайте учетную запись"
        )
    if user.email_verified:
        raise HTTPException(
            status.HTTP_304_NOT_MODIFIED,
            "Электронная почта пользователя уже подтверждена!",
        )
    user.email_verified = True
    user.is_active = True
    session.commit()

    return True


async def resend_verification_email(
    request: Request,
    email: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession,
):
    user = await get_user_by_email(email, session)

    if not user:
        raise HTTPException(
            401, "Пользователь с таким адресом электронной почты не существует!"
        )
    if user.email_verified:
        raise HTTPException(400, "Электронная почта уже проверена!")

    send_verification_email(request, email, background_tasks)

    return {"msg": "Письмо с подтверждением отправлено повторно!"}


async def reset_password(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str,
):
    token = auth.encode_reset_token(email)

    email = schemas.EmailSchema(
        email=[email],
        body={
            "reset_link": f"{request.base_url}reset-password-confirm?token={token}",
            "company_name": settings.PROJECT_TITLE,
        },
    )

    send_mail(
        background_tasks=background_tasks,
        subject=f"{settings.PROJECT_TITLE} Password Reset",
        email=email,
        template_name="reset_password.html",
    )

    return True
