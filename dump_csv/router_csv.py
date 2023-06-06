from datetime import datetime
from pathlib import Path
from typing import Annotated
import os, csv
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

from sqlalchemy.orm import Session
from sqlalchemy.future import select

from user.views import get_active_user
from config.dependency import get_db

from models import models

from . import schemas


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


def query_user_id(
    owner_item_id: int,
    db: Session = Depends(get_db),
):
    stmt = db.execute(
        select(models.Item).where(models.Item.owner_item_id == owner_item_id)
    )
    result = stmt.scalars().all()
    return result


@router.get("/dump-item")
def export_csv(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    detal = query_user_id(db=db, owner_item_id=current_user.id)

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
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse("import_csv.html", {"request": request})


import tempfile


@router.post("/import-csv")
def import_csv(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
    url_f: UploadFile = File(...),
):
    db.query(models.Item).filter(models.Item.owner_item_id == current_user.id).delete()

    # save_path = "./static/csv"
    # file_path = f"{save_path}/{url_file.filename}"

    temp = tempfile.NamedTemporaryFile(delete=False)
    print("temp name..", temp.name)

    contents = url_f.file.read()

    with temp as csvf:
        csvf.write(contents)

    url_f.file.close()

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
        db.add_all(obj)
        db.commit()
        # ..
        csvfile.close()
        Path.unlink(f"{temp.name}")

        return responses.RedirectResponse(
            "/item-list", status_code=status.HTTP_302_FOUND
        )
