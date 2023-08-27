
from datetime import datetime
from pathlib import Path
from typing import Annotated

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

from pydantic import EmailStr

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from user.views import get_active_user
from config.dependency import get_db

from models import models

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/create-item")
def get_create_item(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
):
    msg = ""
    if "msg" in request.query_params:
        msg = request.query_params["msg"]
        return templates.TemplateResponse(
            "item/create.html", {"request": request, "msg": msg}
        )
    return templates.TemplateResponse("item/create.html", {"request": request})


@router.post("/create-item")
async def create_item(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    created_at: datetime = datetime.now(),
    db: Session = Depends(get_db),
):

    exists = db.query(
        models.Item
    ).filter(models.Item.title == title).first()

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

        i = schemas.ItemBase(
            title=title, description=description
        )
        obj = await views.create_not_img_item(
            owner_item_id=current_user.id, created_at=created_at, obj_in=i, db=db,
        )
        return responses.RedirectResponse(
            f"/item-detail/{ obj.id }/?msg=sucesso..!",
            status_code=status.HTTP_302_FOUND
        )

    img = schemas.ItemCreate(
        title=title, description=description, image_url=image_url
    )

    upload = await views.img_creat(category, image_url)

    obj_img = await views.create_new_item(
        image_url=upload, owner_item_id=current_user.id, created_at=created_at, obj_in=img, db=db,
    )

    return responses.RedirectResponse(
        f"/item-detail/{ obj_img.id }/?msg=sucesso..!",
        status_code=status.HTTP_302_FOUND
    )


# ...update


@router.get("/update-item/{id}")
async def get_update(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    obj = await views.retreive_item(id=id, db=db)
    if obj.owner_item_id == current_user.id:
        return templates.TemplateResponse(
            "item/update.html",
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


@router.post("/update-item/{id}")
async def update(
    id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(""),
    image_url: UploadFile = File(""),
    delete_bool: bool = Form(False),
    modified_at: datetime = datetime.now(),
    db: Session = Depends(get_db),
):

    obj = await views.retreive_item(id=id, db=db)

    if image_url.filename == "" or category == "":

        i = schemas.ItemBase(
            title=title,
            description=description,
            modified_at=modified_at,
        )
        await views.update_item(
            id=id, modified_at=modified_at, obj_in=i,  db=db,
        )

        if delete_bool is True:

            if Path(f".{obj.image_url}").exists():
                Path.unlink(f".{obj.image_url}")

            img_del = schemas.ImgDel(
                image_url=image_url,
                modified_at=modified_at,
            )
            await views.img_del(
                id=id, image_url="", modified_at=modified_at, obj_in=img_del, db=db,
            )

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

    await views.img_update_item(
        id=id, image_url=upload, modified_at=modified_at, obj_in=img,  db=db
    )
    return responses.RedirectResponse(
        f"/item-detail/{id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...delete


@router.get("/list-item-delete")
def list_item_delete(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    owner_item_id=current_user.id
    obj_list = views.list_user_item(owner_item_id, db)

    return templates.TemplateResponse(
        "item/list_delete.html", {"request": request, "obj_list": obj_list}
    )


@router.get("/delete-item/{id}")
async def get_delete(
    id: int, request: Request, db: Session = Depends(get_db)
):

    obj = await views.retreive_item(id=id, db=db)

    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "obj": obj}
    )


@router.post("/delete-item/{id}")
async def delete_item(
    id: str,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    obj = await views.retreive_item(id=id, db=db)

    if obj.owner_item_id == current_user.id or current_user.is_admin:
        await views.item_delete(id=id, db=db)

        return responses.RedirectResponse(
            "/list-item-delete/", status_code=status.HTTP_302_FOUND
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


# ...list


@router.get("/item-list")
def item_list(
    request: Request,
    msg: str = None,
    db: Session = Depends(get_db),
):

    obj_list = views.list_item(db=db)

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/list-user-item")
def user_item_list(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    msg: str = None,
    db: Session = Depends(get_db),
):

    obj_list = views.list_user_item(
        owner_item_id=current_user.id, db=db
    )

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


# ...detail


@router.get("/item-detail/{id}")
async def item_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    obj = await views.retreive_item(id=id, db=db)

    # ...
    cmt_list = db.query(
        models.Comment
    ).filter(models.Comment.cmt_item_id == id)

    # ...
    obj_like = db.query(
        models.Like
    ).filter(models.Like.like_item_id == id)
    total_like = obj_like.count()

    # ...
    obj_dislike = db.query(
        models.Dislike
    ).filter(models.Dislike.dislike_item_id == id)
    total_dislike = obj_dislike.count()
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
