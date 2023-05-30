from datetime import datetime

from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Form,
    responses,
)

from fastapi.params import Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from models import models
from config.dependency import get_db
from user.views import get_active_user

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/item-detail/{id}/comment")
def get_create_comment(
    request: Request,
    current_user: models.User = Depends(get_active_user),
):

    if current_user:
        return templates.TemplateResponse(
            "comment/create_comment.html",
            {"request": request},
        )
    return False

@router.post("/item-detail/{id}/comment")
async def create_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
    opinion_expressed: str = Form(...),
    created_at: datetime = datetime.now(),
):

    i = schemas.CmtCreate(
        opinion_expressed=opinion_expressed, created_at=created_at
    )
    await views.comment_create(
        db=db, obj_in=i, cmt_user_id=current_user.id, cmt_item_id=id
    )
    return responses.RedirectResponse(
        f"/item-detail/{id}?msg=sucesso..!",
        status_code=status.HTTP_302_FOUND
    )


# ...


@router.get("/update-comment/{id}")
def get_update_comment(
    id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
):
    cmt_user_id = current_user.id
    cmt = views.retreive_cmt(id=id, db=db)

    return templates.TemplateResponse(
        "comment/up_comment.html",
        {"request": request, "id": id, "cmt_user_id": cmt_user_id, "cmt": cmt},
    )


@router.post("/update-comment/{id}")
async def update_comment(
    id: str,
    db: Session = Depends(get_db),
    opinion_expressed: str = Form(...),
    modified_at: datetime = datetime.now(),
):
    cmt = schemas.CmtUpdate(
        opinion_expressed=opinion_expressed, modified_at=modified_at
    )
    await views.up_comment(id=id, cmt=cmt, db=db, modified_at=modified_at)

    return responses.RedirectResponse(
        f"/item-detail/{id}", status_code=status.HTTP_302_FOUND
    )


@router.get("/delete-comment/{id}")
def get_delete_comment(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_active_user),
):
    cmt_user_id = current_user.id
    obj = views.retreive_cmt(id=id, db=db)

    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "cmt_user_id": cmt_user_id, "obj": obj}
    )


@router.post("/delete-comment/{id}")
async def delete_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_active_user),
):
    obj = views.retreive_cmt(id=id, db=db)

    if obj.cmt_user_id == current_user.id or current_user.is_admin:
        views.comment_delete(id=id, db=db)

        return responses.RedirectResponse(
            "/item-list", status_code=status.HTTP_302_FOUND
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )
