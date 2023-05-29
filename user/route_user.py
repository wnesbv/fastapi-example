
from fastapi import (
    APIRouter,
    Depends,
    Request,
    Form,
    responses,
    status,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from models import models
from account.auth import auth

from spare_parts import user
from config.dependency import get_db
from . import schemas


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/update-user/{id}")
def get_update(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        user.get_active_user
    ),
):

    obj = user.retreive_user(id=id, db=db)

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
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        user.get_active_user
    ),
    name: str = Form(...),
    password: str = Form(...),
):

    user_details = schemas.UserUpdate(
        name=name, password=password
    )
    await user.update_user(
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

    obj_list = user.list_user(db=db)

    return templates.TemplateResponse(
        "user/list.html",
        {
            "request": request,
            "obj_list": obj_list,
        }
    )


@router.get("/user-detail/{id}")
def user_detail(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
):

    obj = user.retreive_user(id=id, db=db)

    return templates.TemplateResponse(
        "user/detail.html",
        {
            "request": request,
            "obj": obj,
        }
    )
