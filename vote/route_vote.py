
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form, responses, status
from fastapi.templating import Jinja2Templates

from pydantic import EmailStr
from sqlalchemy.orm import Session

from config.dependency import get_db
from user.views import get_active_user

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/like/{id}")
def get_like_create(
    id: str,
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    like_user_id=current_user.id
    if not views.retreive_like(
        current_user=like_user_id,
        id=id,
        db=db,
    ):

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
    id: str,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
    upvote: bool = Form(True),
    created_at: datetime = datetime.now(),
):

    i = schemas.LikeChoose(
        upvote=upvote, created_at=created_at
    )

    await views.like_add(
        db=db,
        like_in=i,
        like_item_id=id,
        like_user_id=current_user.id,
    )

    return responses.RedirectResponse(
        f"/item-detail/{ id }", status_code=status.HTTP_302_FOUND
    )


# ...


@router.get("/dislike/{id}/")
def get_dislike_create(
    id: str,
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    dislike_user_id = current_user.id
    if not views.retreive_dislike(
        current_user=dislike_user_id,
        id=id,
        db=db
    ):

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
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
    downvote: bool = Form(False),
    created_at: datetime = datetime.now(),
):

    i = schemas.DislikeChoose(
        downvote=downvote, created_at=created_at
    )

    await views.dislike_add(
        db=db,
        dislike_in=i,
        dislike_item_id=id,
        dislike_user_id=current_user.id
    )

    return responses.RedirectResponse(
        f"/item-detail/{ id }",
        status_code=status.HTTP_302_FOUND
    )
