
from fastapi import (
    BackgroundTasks,
    APIRouter,
    Depends,
    Request,
    Response,
    responses,
    Form,
    status,
)
from pydantic import EmailStr
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from config.dependency import get_db
from user import schemas as user_schemas
from spare_parts.user import get_active_user

from models import models
from .auth import auth
from . import views
from . import schemas


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/register", response_model=user_schemas.UserRegister)
def get_register(request: Request):

    return templates.TemplateResponse(
        "auth/register.html", {"request": request}
    )


@router.post("/register", response_model=user_schemas.UserCreate)
async def register(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    email: EmailStr = Form(...),
    password: str = Form(...),
):

    user = user_schemas.UserCreate(email=email, password=password)
    obj = views.create_user(
        user=user,
        background_tasks=background_tasks,
        request=request,
        db=db,
    )

    return responses.RedirectResponse(
        f"/user-detail/{obj.id}", status_code=status.HTTP_302_FOUND
    )


# ...


@router.get("/login")
def get_login(request: Request):

    return templates.TemplateResponse("auth/login.html",
        {"request": request}
    )


@router.post("/login")
async def login(
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):

    user = schemas.LoginDetails(
        email=email, password=password
    )
    response = responses.RedirectResponse(
        "/", status_code=status.HTTP_302_FOUND
    )
    response.token = views.login_user(
        user, db, bg_tasks, request, response=response
    )
    return response


@router.get("/verify-email")
def confirmation_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
):

    response = views.account_verify_email(token, db)
    msg = "Электронная почта успешно подтверждена"
    response = templates.TemplateResponse(
        "index.html", {"request": request, "msg": msg}
    )
    return response


# ...


@router.get("/reset-password/")
def get_reset_password(
    request: Request,
):

    return templates.TemplateResponse(
        "auth/reset-password.html",
        {"request": request},
    )


@router.post("/reset-password/")
async def post_reset_password(
    bg_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
):
    user = views.get_user_by_email(email, db)

    if user:
        views.reset_password(bg_tasks=bg_tasks, request=request, email=email)

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


@router.get("/reset-password-confirm/")
def get_reset_password_confirm(
    request: Request,
):

    return templates.TemplateResponse(
        "auth/reset-password-confirm.html",
        {"request": request},
    )


@router.post("/reset-password-confirm/")
async def reset_password_confirm(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
    password: str = Form(...),
):

    user_details = schemas.ResetPasswordDetails(password=password)

    email = auth.verify_reset_token(token)
    user = views.get_user_by_email(email, db)

    if user:
        pswd = auth.hash_password(password)

        existing_user = db.query(
            models.User
        ).filter(models.User.email == email)

        user_details.__dict__.update(password=pswd)
        existing_user.update(user_details.__dict__)
        db.commit()


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


@router.get("/me", response_model=user_schemas.User)
def get_user_profile(
    request: Request,
    current_user: user_schemas.User = Depends(get_active_user)
):

    return templates.TemplateResponse("index.html",
        {"request": request, "current_user": current_user}
    )
