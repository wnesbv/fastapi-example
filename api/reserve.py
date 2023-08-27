from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated
import json

from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Request,
    Response,
    responses,
    Form,
    status,
)

from pydantic import EmailStr

from fastapi.templating import Jinja2Templates
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from user.views import get_active_user
from config.dependency import get_db
from config.settings import settings

from models import models, reserverent

from item import schemas as item_schemas
from reserve import schemas, views


router = APIRouter(prefix="/docs", tags=["Reserve"])


@router.post("/reserve-add", response_model=schemas.ReserveAdd)
async def reserve_add(
    time_end: datetime = Form(...),
    time_start: datetime = Form(...),
):

    if time_start >= time_end or time_start < datetime.now():
        return responses.PlainTextResponse("please enter proper dates")

    generated = [
        time_start + timedelta(days=x)
        for x in range(0, (time_end - time_start).days + 1)
    ]

    reserve_period = []
    for period in generated:
        reserve_period.append(period.strftime(settings.DATE))

    reserve_period = str(reserve_period)
    print("type, reserve_period", type(reserve_period))

    start = datetime.strftime(time_start, settings.DATE_T)
    end = datetime.strftime(time_end, settings.DATE_T)

    # ..
    payload = {
        "reserve_period": reserve_period,
        "start": start,
        "end": end,
    }
    reserve = json.dumps(payload)
    response = responses.JSONResponse(reserve)
    response.set_cookie("reserve", reserve)
    return response


async def get_token_reserve(
    request: Request,
):
    if not request.cookies.get("reserve"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="not reserve token ..!",
        )
    token_get = request.cookies.get("reserve")
    token_loads = json.loads(token_get)

    return token_loads


@router.get("/reserve/choice")
async def get_reserve_choice(
    request: Request,
    db: Session = Depends(get_db),
):
    token = await get_token_reserve(request)

    start = token["start"]
    end = token["end"]
    reserve_period = token["reserve_period"]

    time_start = datetime.strptime(start, settings.DATE_T)
    time_end = datetime.strptime(end, settings.DATE_T)

    obj_item = await views.period_item(time_start, time_end, db)
    not_item = await views.not_period(db)


    obj_in = [
        item_schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )
        for i in obj_item
    ]

    obj_not = [
        item_schemas.ListItem(
            id=i.id,
            title=i.title,
            description=i.description,
            image_url=i.image_url,
            created_at=i.created_at,
            modified_at=i.modified_at,
            owner_item_id=i.owner_item_id,
        )
        for i in not_item
    ]
    print("obj_in..", obj_in)
    print("obj_not..", obj_not)
    return (obj_in, obj_not)


@router.get("/reserve-details/{id}")
async def get_reserve_details(
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    stmt = db.execute(select(models.Item).where(models.Item.id == id))
    i = stmt.scalars().first()

    obj = item_schemas.ListItem(
        id=i.id,
        title=i.title,
        description=i.description,
        image_url=i.image_url,
        created_at=i.created_at,
        modified_at=i.modified_at,
        owner_item_id=i.owner_item_id,
    )

    return obj


@router.post("/reserve-details_add/{id}")
async def reserve_details(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    description: str = Form(...),
    db: Session = Depends(get_db),
):

    token = await get_token_reserve(request)

    start = token["start"]
    end = token["end"]
    reserve_period = token["reserve_period"]

    time_start = datetime.strptime(start, settings.DATE_T)
    time_end = datetime.strptime(end, settings.DATE_T)

    # ..
    query = insert(reserverent.ReserveRentFor).values(
        time_start=time_start,
        time_end=time_end,
        description=description,
        rrf_us_id=current_user.id,
        rrf_tm_id=id,
        created_at=datetime.now(),
    )
    db.execute(query)
    db.commit()
    # ..
    return {"msg": "Ok..!"}


@router.get("/list-reserve")
async def list_user_reserve(
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    rrf_us_id = current_user.id
    obj_list = await views.rrf_list(rrf_us_id, db)

    rrf_user_list = [
        schemas.ReserveList(
            id=i.id,
            description=i.description,
            time_start=i.time_start,
            time_end=i.time_end,
            reserve_time=i.reserve_time,
            created_at=i.created_at,
            modified_at=i.modified_at,
            rrf_us_id=i.rrf_us_id,
            rrf_tm_id=i.rrf_tm_id,
        )
        for i in obj_list
    ]
    return rrf_user_list


@router.get("/details-reserve/{id}")
async def details_reserve(
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    rrf_us_id = current_user.id
    i = await views.rrf_details(id, rrf_us_id, db)

    obj = schemas.ReserveList(
        id=i.id,
        description=i.description,
        time_start=i.time_start,
        time_end=i.time_end,
        reserve_time=i.reserve_time,
        created_at=i.created_at,
        modified_at=i.modified_at,
        rrf_us_id=i.rrf_us_id,
        rrf_tm_id=i.rrf_tm_id,
    )


    return obj
