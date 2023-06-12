
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

from sqlalchemy.orm import Session

from models import models
from account.auth import auth

from config.dependency import get_db
from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/update-user/{id}")
def get_update(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(views.get_active_user)],
    db: Session = Depends(get_db),
):

    obj = views.retreive_user(id=id, db=db)

    if obj.id == current_user.id or current_user.is_admin:

        return templates.TemplateResponse(
            "user/update.html",
            {
                "request": request,
                "id": id,
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
    current_user: Annotated[EmailStr, Depends(views.get_active_user)],
    id: int,
    name: str = Form(...),
    password: str = Form(...),
    modified_at: datetime = datetime.now(),
    db: Session = Depends(get_db),
):

    user_details = schemas.UserUpdate(
        name=name, password=password, modified_at=modified_at,
    )
    await views.update_user(
        id=id,
        db=db,
        user_details=user_details,
        current_user=current_user,
        password=auth.hash_password(password)
    )

    return responses.RedirectResponse(
        f"/user-detail/{id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...list detail ...


@router.get("/user-list/")
def user_list(
    request: Request,
    db: Session = Depends(get_db),
):

    obj_list = views.list_user(db=db)

    return templates.TemplateResponse(
        "user/list.html",
        {
            "request": request,
            "obj_list": obj_list,
        }
    )


@router.get("/user-detail/{id}")
def user_detail(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
):

    obj = views.retreive_user(id=id, db=db)
    obj_item = views.count_user_item(id=id, db=db)
    count_item = len(obj_item)
    return templates.TemplateResponse(
        "user/detail.html",
        {
            "request": request,
            "obj": obj,
            "obj_item": obj_item,
            "count_item": count_item,
        }
    )
