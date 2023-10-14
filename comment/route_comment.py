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

from fastapi.params import Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from config.dependency import get_session
from user.views import access_user_id
from options_select.opt import in_all, left_right_first, left_right_all

from models import models

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/item-detail/{id}/comment")
async def get_create_comment(
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)]
):
    if current_user:
        return templates.TemplateResponse(
            "comment/create_comment.html",
            {"request": request, "current_user": current_user},
        )
    return responses.RedirectResponse("/login")


@router.post("/item-detail/{id}/comment")
async def create_comment(
    id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
    opinion_expressed: str = Form(...),
    created_at: datetime = datetime.now(),
):

    if current_user:
        obj_in = schemas.CmtCreate(
            opinion_expressed=opinion_expressed, created_at=created_at
        )
        await views.comment_create(
            current_user.id, id, obj_in, session
        )
        return responses.RedirectResponse(
            f"/item-detail/{ id }?msg=sucesso..!",
            status_code=status.HTTP_302_FOUND
        )
    return responses.RedirectResponse("/login")


# ...update
@router.get("/item-detail/{i_id}/update-comment/{cmt_id}")
async def get_update_comment(
    request: Request,
    cmt_id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):

    i = await left_right_first(session, models.Comment, models.Comment.id, cmt_id)

    if i.cmt_user_id == current_user.id or current_user.is_admin:

        return templates.TemplateResponse(
            "comment/up_comment.html",
            {"request": request, "current_user": current_user, "i": i},
        )
    return responses.RedirectResponse("/login")


@router.post("/item-detail/{id}/update-comment/{cmt_id}")
async def update_comment(
    id: int,
    cmt_id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    opinion_expressed: str = Form(...),
    modified_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):

    i = await left_right_first(session, models.Comment, models.Comment.id, cmt_id)

    if i.cmt_user_id == current_user.id or current_user.is_admin:

        obj_in = schemas.CmtUpdate(
            opinion_expressed=opinion_expressed, modified_at=modified_at
        )
        await views.up_comment(cmt_id, modified_at, obj_in, session)

        return responses.RedirectResponse(
            f"/item-detail/{id}", status_code=status.HTTP_302_FOUND
        )
    return responses.RedirectResponse("/login")

# ...delete


@router.get("/item-detail/{id}/delete-comment/{cmt_id}")
async def get_delete_comment(
    request: Request,
    cmt_id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):

    i = await left_right_first(session, models.Comment, models.Comment.id, cmt_id)

    if i.cmt_user_id == current_user.id or current_user.is_admin:

        return templates.TemplateResponse(
            "item/delete.html", {"request": request, "current_user": current_user, "i": i}
        )
    return responses.RedirectResponse("/login")


@router.post("/item-detail/{id}/delete-comment/{cmt_id}")
async def delete_comment(
    id: int,
    cmt_id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):

    i = await left_right_first(session, models.Comment, models.Comment.id, cmt_id)

    if i.cmt_user_id == current_user.id or current_user.is_admin:

        await views.comment_delete(cmt_id, current_user.id, session)

        return responses.RedirectResponse(
            f"/item-detail/{id}", status_code=status.HTTP_302_FOUND
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )
