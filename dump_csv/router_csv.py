from datetime import datetime
from pathlib import Path
from typing import Annotated
import os, csv
import tempfile
from pydantic import EmailStr

from sqlalchemy import delete
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

from user.views import get_active_user
from config.dependency import get_session
from options_select.opt import in_all, left_right_first, left_right_all

from models import models

from . import schemas


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


@router.get("/dump-item")
async def export_csv(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
):

    detal = await left_right_all(
        session, models.Item, models.Item.owner_item_id, current_user.id
    )

    file_time = datetime.now()
    directory = BASE_DIR / f"static/csv/{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    filename = f"{file_time.strftime('%Y-%m-%d-%H-%M-%S')}.csv"

    with open(directory, "w", encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(
            [
                "id",
                "title",
                "description",
                "image_url",
                "created_at",
                "modified_at",
                "owner_item_id",
            ]
        )
        for i in detal:
            spamwriter.writerow(
                [
                    i.id,
                    i.title,
                    i.description,
                    i.image_url,
                    i.created_at,
                    i.modified_at,
                    i.owner_item_id,
                ]
            )

        return responses.RedirectResponse(
            f"/static/csv/{filename}", status_code=status.HTTP_302_FOUND
        )


# ...import


@router.get("/import-csv")
async def ge_import_csv(
    request: Request,
):
    return templates.TemplateResponse("import_csv.html", {"request": request})



@router.post("/import-csv")
async def import_csv(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    session: AsyncSession = Depends(get_session),
    url_file: UploadFile = File(...),
):

    query = delete(models.Item).where(models.Item.owner_item_id == current_user.id)

    await session.execute(query)

    # save_path = "./static/csv"
    # file_path = f"{save_path}/{url_file.filename}"

    temp = tempfile.NamedTemporaryFile(delete=False)
    print("temp name..", temp.name)

    contents = url_file.file.read()

    with temp as csvf:
        csvf.write(contents)

    url_file.file.close()

    with open(temp.name, "r", encoding="utf-8") as csvfile:
        obj = [
            models.Item(
                **{
                    "id": int(i["id"]),
                    "title": i["title"],
                    "description": i["description"],
                    "image_url": i["image_url"],
                    "created_at": datetime.now(),
                    "owner_item_id": current_user.id,
                }
            )
            for i in csv.DictReader(csvfile)
        ]
        # ..
        session.add_all(obj)
        await session.commit()
        # ..
        csvfile.close()
        Path.unlink(f"{ temp.name }")

        return responses.RedirectResponse(
            "/item-list", status_code=status.HTTP_302_FOUND
        )
