
from datetime import datetime

from fastapi import BackgroundTasks, HTTPException, status, Request, Response

from pydantic import EmailStr
from sqlalchemy.orm import Session

from config.settings import settings
from config.mail import send_mail
from models import models
from user.schemas import UserCreate, UserRegister
from .auth import auth
from . import schemas


async def get_user_by_email(email: str, db: Session):

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    return user


def generate_verification_email_link(request: Request, email):

    email_token = auth.encode_verification_token(email)
    base_url = request.base_url
    verification_link = f"{base_url}verify-email?token={email_token}"

    return verification_link


def send_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email: EmailStr,
):

    verification_link = generate_verification_email_link(
        request, email=email
    )

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


# ...


async def create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    user: UserCreate,
    password: str,
    db: Session,
):

    old_user = await get_user_by_email(email=user.email, db=db)
    if old_user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User with this email already exists"
        )

    send_verification_email(
        request=request,
        background_tasks=background_tasks,
        email=user.email,
    )

    new = models.User(
        **user.dict(), password=password
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new


def api_create_user(
    request: Request,
    background_tasks: BackgroundTasks,
    obj_in: UserCreate,
    password: str,
    created_at: datetime,
    db: Session,
):
    print("useremail", obj_in.email)
    user = db.query(models.User).filter(
        models.User.email == obj_in.email
    ).first()

    if user:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "User with this email already exists"
        )

    new = models.User(
        **obj_in.dict(), password=password, created_at=created_at
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    send_verification_email(
        request=request,
        background_tasks=background_tasks,
        email=obj_in.email,
    )

    return new


async def login_user(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    user_details: schemas.LoginDetails,
    db: Session,
):

    user = await get_user_by_email(email=user_details.email, db=db)
    print("user_details", user_details.password)

    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "User with this email doesn't exist!"
        )

    if not auth.verify_password(user_details.password, user.password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Incorrect password!"
        )

    if not user.email_verified:
        send_verification_email(request, background_tasks, user_details.email)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Электронная почта не подтверждена. Проверьте свою почту, чтобы узнать, как пройти верификацию.",
        )
    # ...
    access_token = auth.encode_token(user.email, user)

    response.set_cookie(
        "access_token", access_token, httponly=True
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


# ...


async def account_verify_email(
    token: str,
    db: Session,
):

    email = auth.verify_email(token)
    user = await get_user_by_email(email, db)
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
    db.commit()

    return True


async def resend_verification_email(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str,
    db: Session,
):
    user = await get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            401, "Пользователь с таким адресом электронной почты не существует!"
        )
    if user.email_verified:
        raise HTTPException(400, "Электронная почта уже проверена!")

    send_verification_email(request, background_tasks, email)

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
