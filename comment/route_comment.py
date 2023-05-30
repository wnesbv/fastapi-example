from datetime import datetime

from typing import Annotated

from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Request,
    Form,
    responses,
)

from pydantic import EmailStr

from fastapi.params import Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from config.dependency import get_db
from user.views import get_active_user

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/item-detail/{id}/comment")
def get_create_comment(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)]
):

    return templates.TemplateResponse(
        "comment/create_comment.html",
        {"request": request, "current_user": current_user},
    )


@router.post("/item-detail/{id}/comment")
async def create_comment(
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
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


# ...update


@router.get("/item-detail/{I_id}/update-comment/{cmt_id}")
def get_update_comment(
    cmt_id: int,
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    cmt = views.retreive_cmt(id=cmt_id, db=db)

    return templates.TemplateResponse(
        "comment/up_comment.html",
        {"request": request, "current_user": current_user, "cmt": cmt},
    )


@router.post("/item-detail/{id}/update-comment/{cmt_id}")
async def update_comment(
    id: int,
    cmt_id: int,
    db: Session = Depends(get_db),
    opinion_expressed: str = Form(...),
    modified_at: datetime = datetime.now(),
):
    cmt = schemas.CmtUpdate(
        opinion_expressed=opinion_expressed, modified_at=modified_at
    )
    await views.up_comment(id=cmt_id, cmt=cmt, db=db, modified_at=modified_at)

    return responses.RedirectResponse(
        f"/item-detail/{id}", status_code=status.HTTP_302_FOUND
    )


# ...delete


@router.get("/item-detail/{id}/delete-comment/{cmt_id}")
def get_delete_comment(
    cmt_id: int,
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    obj = views.retreive_cmt(id=cmt_id, db=db)

    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "current_user": current_user, "obj": obj}
    )


@router.post("/item-detail/{id}/delete-comment/{cmt_id}")
async def delete_comment(
    id: int,
    cmt_id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):

    obj = views.retreive_cmt(id=cmt_id, db=db)

    if obj.cmt_user_id == current_user.id or current_user.is_admin:
        await views.comment_delete(id=cmt_id, db=db)

        return responses.RedirectResponse(
            f"/item-detail/{id}", status_code=status.HTTP_302_FOUND
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )
