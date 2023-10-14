
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, responses, status
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from config.dependency import get_session
from user.views import access_user_id

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/like/{id}")
async def get_like_create(
    id: str,
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):

    if not await views.retreive_like(id, current_user.id, session):

        return templates.TemplateResponse(
            "item/like.html",
            {"request": request},
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "have you already voted..!",
        },
    )


@router.post("/like/{id}")
async def like_create(
    id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    upvote: bool = True,
    created_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):

    obj_in = schemas.LikeChoose(
        upvote=upvote, created_at=created_at
    )

    await views.like_add(id, current_user.id, obj_in, session)

    return responses.RedirectResponse(
        f"/item-detail/{ id }", status_code=status.HTTP_302_FOUND
    )


# ...
@router.get("/dislike/{id}/")
async def get_dislike_create(
    id: str,
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):

    like = await views.retreive_dislike(id, current_user.id, session
    )
    if not like:

        return templates.TemplateResponse(
            "item/dislike.html",
            {"request": request},
        )

    return templates.TemplateResponse(
        "components/error.html",
        {
            "request": request,
            "message": "have you already voted..!",
        },
    )


@router.post("/dislike/{id}/")
async def dislike_create(
    id: str,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
    downvote: bool = False,
    created_at: datetime = datetime.now(),
):

    obj_in = schemas.DislikeChoose(
        downvote=downvote, created_at=created_at
    )

    await views.dislike_add(id, current_user.id, obj_in, session)

    return responses.RedirectResponse(
        f"/item-detail/{ id }",
        status_code=status.HTTP_302_FOUND
    )
