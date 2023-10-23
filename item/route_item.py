
from pathlib import Path
from datetime import datetime
from typing import Annotated

from sqlalchemy.future import select

from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Request,
    responses,
    Form,
    File,
    UploadFile,
    status,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from config.dependency import get_session
from user.views import access_user_id
from options_select.opt import in_all, left_right_first, left_right_all

from models import models

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/create-item")
async def get_create_item(
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
):
    if current_user:
        msg = ""
        if "msg" in request.query_params:
            msg = request.query_params["msg"]
            return templates.TemplateResponse(
                "item/create.html", {"request": request, "msg": msg}
            )
        return templates.TemplateResponse("item/create.html", {"request": request})
    return responses.RedirectResponse("/login")


@router.post("/create-item")
async def create_item(
    current_user: Annotated[int, Depends(access_user_id)],
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    created_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):
    exists = await left_right_first(session, models.Item, models.Item.title, title)

    if exists:
        return responses.RedirectResponse(
            "/create-item?msg=such a title already exists..!",
            status_code=status.HTTP_302_FOUND,
        )
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="name already registered..!"
        # )

    if image_url.filename == "" or category == "":

        obj_in = schemas.ItemBase(title=title, description=description)

        obj = await views.create_not_img_item(
            current_user.id,
            created_at,
            obj_in,
            session,
        )
        response = responses.RedirectResponse(
            f"/item-detail/{ obj.id }",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(
            key="message",
            value="sucesso..!",
            path=(f"/item-detail/{ obj.id }"),
            max_age=int(10),
            httponly=True,
        )
        return response
    # ..
    obj_in = schemas.ItemCreate(
        title=title, description=description, image_url=image_url
    )

    upload = await views.img_creat(category, image_url)
    obj_img = await views.create_new_item(
        upload,
        current_user.id,
        created_at,
        obj_in,
        session,
    )

    return responses.RedirectResponse(
        f"/item-detail/{ obj_img.id }/?msg=sucesso..!",
        status_code=status.HTTP_302_FOUND,
    )


# ...detail


@router.get("/item-detail/{id}")
async def item_detail(
    id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    # ..
    obj = await left_right_first(session, models.Item, models.Item.id, id)

    # ..
    cmt_list = await left_right_all(
        session, models.Comment, models.Comment.cmt_item_id, id
    )
    # ..
    stmt = await session.execute(
        select(models.Like.like_item_id).where(models.Like.like_item_id == id)
    )
    obj_like = stmt.scalars().all()
    # ..
    total_like = len(list(obj_like))

    # ...
    stmt = await session.execute(
        select(models.Dislike.dislike_item_id).where(
            models.Dislike.dislike_item_id == id
        )
    )
    obj_dislike = stmt.scalars().all()
    # ..
    total_dislike = len(list(obj_dislike))

    # ...
    msg = ""
    if "msg" in request.query_params:
        msg = request.query_params["msg"]

        return templates.TemplateResponse(
            "item/detail.html",
            {
                "request": request,
                "msg": msg,
                "obj": obj,
                "cmt_list": cmt_list,
                "total_like": total_like,
                "total_dislike": total_dislike,
            },
        )

    return templates.TemplateResponse(
        "item/detail.html",
        {
            "request": request,
            "obj": obj,
            "cmt_list": cmt_list,
            "total_like": total_like,
            "total_dislike": total_dislike,
        },
    )


# ...update


@router.get("/update-item/{id}")
async def get_update(
    request: Request,
    id: int,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):
    obj = await left_right_first(session, models.Item, models.Item.id, id)
    if obj.owner_item_id == current_user:
        return templates.TemplateResponse(
            "item/update.html",
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


@router.post("/update-item/{id}")
async def update(
    id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    delete_bool: bool = Form(False),
    modified_at: datetime = datetime.now(),
    session: AsyncSession = Depends(get_session),
):
    obj = await left_right_first(session, models.Item, models.Item.id, id)

    if image_url.filename == "" or category == "":
        i = schemas.ItemBase(
            title=title,
            description=description,
            modified_at=modified_at,
        )
        await views.update_item(id, modified_at, i, session)

        if delete_bool is True:
            if Path(f".{obj.image_url}").exists():
                Path.unlink(f".{obj.image_url}")

            img_not = schemas.ImgDel(
                modified_at=modified_at,
            )
            await views.img_del(id, modified_at, img_not, session)

            return responses.RedirectResponse(
                f"/item-detail/{id }",
                status_code=status.HTTP_302_FOUND,
            )
        return responses.RedirectResponse(
            f"/item-detail/{id }",
            status_code=status.HTTP_302_FOUND,
        )

    img = schemas.ItemCreate(
        title=title,
        description=description,
        image_url=image_url,
        modified_at=modified_at,
    )
    upload = await views.img_creat(category, image_url)

    await views.img_update_item(id, upload, modified_at, img, session)
    return responses.RedirectResponse(
        f"/item-detail/{id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...delete


@router.get("/list-item-delete")
async def list_item_delete(
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):
    if current_user:
        obj_list = await left_right_all(
            session, models.Item, models.Item.owner_item_id, current_user.id
        )
        return templates.TemplateResponse(
            "item/list_delete.html", {"request": request, "obj_list": obj_list}
        )
    return responses.RedirectResponse("/login")


@router.get("/delete-item/{id}")
async def get_delete(
    id: int,
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):
    if current_user:
        obj = await views.item_owner(id, current_user.id, session)

        return templates.TemplateResponse(
            "item/delete.html", {"request": request, "obj": obj}
        )
    return responses.RedirectResponse("/login")


@router.post("/delete-item/{id}")
async def delete_item(
    id: str,
    current_user: Annotated[int, Depends(access_user_id)],
    session: AsyncSession = Depends(get_session),
):
    obj = await views.item_owner(id, current_user.id, session)

    if obj.owner_item_id == current_user.id or current_user.is_admin:
        await views.item_delete(id, current_user.id, session)

        return responses.RedirectResponse(
            "/list-item-delete/", status_code=status.HTTP_302_FOUND
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


# ...list


@router.get("/item-list")
async def item_list(
    request: Request,
    msg: str = None,
    session: AsyncSession = Depends(get_session),
):
    obj_list = await in_all(session, models.Item)

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/list-user-item")
async def user_item_list(
    request: Request,
    current_user: Annotated[int, Depends(access_user_id)],
    msg: str = None,
    session: AsyncSession = Depends(get_session),
):
    obj_list = await left_right_all(
        session, models.Item, models.Item.owner_item_id, current_user.id
    )

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )
