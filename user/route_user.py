
from datetime import datetime
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    responses,
    status,
)

from pydantic import EmailStr

from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from models import models
from account.auth import auth

from config.dependency import get_session
from options_select.opt import in_all

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/update-user/{id}")
async def get_update(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(views.get_active_user)],
    session: AsyncSession = Depends(get_session),
):

    obj = await views.retreive_user(id, session)

    if obj.id == current_user.id or current_user.is_admin:

        return templates.TemplateResponse(
            "user/update.html",
            {
                "request": request,
                "obj": obj,
            },
        )
    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "You are not permitted..!",
        },
    )


@router.post("/update-user/{id}")
async def to_update(
    id: int,
    current_user: Annotated[EmailStr, Depends(views.get_active_user)],
    name: str = Form(...),
    password: str = Form(...),
    modified_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):

    if current_user.id == id or current_user.is_admin:
        user_details = schemas.UserUpdate(
            name=name, password=password, modified_at=modified_at,
        )
        await views.update_user(
            id, auth.hash_password(password), user_details, session
        )
        return responses.RedirectResponse(
            f"/user-detail/{id }",
            status_code=status.HTTP_302_FOUND,
        )


# ...list detail ...


@router.get("/user-list/")
async def user_list(
    request: Request,
    session: AsyncSession = Depends(get_session),
):

    obj_list = await in_all(session, models.User)

    return templates.TemplateResponse(
        "user/list.html",
        {
            "request": request,
            "obj_list": obj_list,
        }
    )


@router.get("/user-detail/{id}")
async def user_detail(
    request: Request,
    id: int,
    session: AsyncSession = Depends(get_session),
):

    obj = await views.retreive_user(id, session)
    obj_item = await views.count_user_item(id, session)
    print("obj_item..", obj_item)
    count_item = len(list(obj_item))
    print("count_item..", count_item)
    return templates.TemplateResponse(
        "user/detail.html",
        {
            "request": request,
            "obj": obj,
            "obj_item": obj_item,
            "count_item": count_item,
        }
    )
