import os
from datetime import datetime

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

from sqlalchemy.orm import Session

from spare_parts import item
from spare_parts.user import get_active_user
from config.dependency import get_db

from models import models

from . import schemas


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/create-item")
def get_create(request: Request):
    msg = ""
    if "msg" in request.query_params:
        msg = request.query_params["msg"]
        return templates.TemplateResponse(
            "item/create.html", {"request": request, "msg": msg}
        )
    return templates.TemplateResponse("item/create.html", {"request": request})


@router.post("/create-item")
async def create(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image_url: UploadFile = File(...),
    created_at: datetime = datetime.now(),
):
    exists = db.query(models.Item).filter(models.Item.title == title).first()

    if exists:
        return responses.RedirectResponse(
            "/create-item?msg=such a title already exists..!",
            status_code=status.HTTP_302_FOUND,
        )
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="name already registered..!"
        # )


    upload = item.img_creat(category, image_url)
    original = upload
    removed = original.replace(".", "", 1)

    i = schemas.ItemCreate(
        title=title, description=description, image_url=image_url, created_at=created_at
    )
    obj = await item.create_new_item(
        db=db, obj_in=i, image_url=removed, owner_item_id=current_user.id,
    )

    return responses.RedirectResponse(
        f"/item-detail/{ obj.id }/?msg=sucesso..!", status_code=status.HTTP_302_FOUND
    )


@router.get("/update-item/{id}")
def get_update(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
):
    obj = item.retreive_item(id=id, db=db)
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
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image_url: UploadFile = File(...),
    modified_at: datetime | None = None,
):

    upload = item.img_creat(category, image_url)
    original = upload
    removed = original.replace(".", "", 1)

    i = schemas.ItemUpdate(
        title=title,
        description=description,
        image_url=removed,
        modified_at=modified_at,
    )
    await item.update_item(
        id=id, obj_in=i, db=db, modified_at=datetime.now()
    )

    return responses.RedirectResponse(
        f"/item-detail/{id }",
        status_code=status.HTTP_302_FOUND,
    )


# ...delete


@router.get("/list-item-delete/")
def list_item_delete(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
):
    obj_list = item.list_user_item(db, owner_item_id=current_user.id)

    return templates.TemplateResponse(
        "item/list_delete.html", {"request": request, "obj_list": obj_list}
    )


@router.get("/delete-item/{id}")
def get_delete(id: int, request: Request, db: Session = Depends(get_db)):
    obj = item.retreive_item(id=id, db=db)

    return templates.TemplateResponse(
        "item/delete.html", {"request": request, "obj": obj}
    )


@router.post("/delete-item/{id}")
async def delete_item(
    id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_active_user),
):
    obj = item.retreive_item(id=id, db=db)

    if obj.owner_item_id == current_user.id or current_user.is_admin:
        item.item_delete(id=id, db=db)

        return responses.RedirectResponse(
            "/list-item-delete/", status_code=status.HTTP_302_FOUND
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not permitted!!!!"
    )


# ...


@router.get("/item-list/")
def item_list(request: Request, db: Session = Depends(get_db), msg: str = None):
    obj_list = item.list_item(db=db)

    return templates.TemplateResponse(
        "item/list.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/item-detail/{id}/")
def item_detail(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    obj = item.retreive_item(id=id, db=db)
    cmt_list = db.query(models.Comment).filter(models.Comment.cmt_item_id == id)

    # ...
    obj_like = db.query(models.Like).filter(models.Like.like_item_id == id)
    total_like = obj_like.count()

    obj_dislike = db.query(models.Dislike).filter(models.Dislike.dislike_item_id == id)
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
