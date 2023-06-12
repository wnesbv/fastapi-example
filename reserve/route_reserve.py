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
    File,
    UploadFile,
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

from . import schemas, views


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/reserve-add")
async def get_reserve_add(request: Request):
    msg = ""
    if "msg" in request.query_params:
        msg = request.query_params["msg"]
        return templates.TemplateResponse(
            "reserve/index.html", {"request": request, "msg": msg}
        )
    return templates.TemplateResponse("reserve/index.html", {"request": request})


@router.post("/reserve-add")
async def reserve_add(request: Request):
    form = await request.form()
    end = form["end"]
    start = form["start"]

    print("end..", type(end))
    print("date..", type(date.today().strftime(settings.DATE)))

    time_start = datetime.strptime(start, settings.DATE_T)
    time_end = datetime.strptime(end, settings.DATE_T)

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

    # ..
    payload = {
        "reserve_period": reserve_period,
        "start": start,
        "end": end,
    }
    reserve = json.dumps(payload)
    response = responses.RedirectResponse(
        "/reserve/choice",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie("reserve", reserve)
    return response


# ...choice


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

    context = {
        "request": request,
        "time_start": time_start,
        "time_end": time_end,
        "reserve_period": reserve_period,
        "obj_item": obj_item,
        "not_item": not_item,
    }
    template = "reserve/choice.html"

    return templates.TemplateResponse(template, context)


@router.get("/reserve-details/{id}")
async def get_reserve_details(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    stmt = db.execute(select(models.Item).where(models.Item.id == id))
    i = stmt.scalars().first()

    token = await get_token_reserve(request)

    start = token["start"]
    end = token["end"]
    reserve_period = token["reserve_period"]

    time_start = datetime.strptime(start, settings.DATE_T)
    time_end = datetime.strptime(end, settings.DATE_T)

    context = {
        "request": request,
        "time_start": time_start,
        "time_end": time_end,
        "reserve_period": reserve_period,
        "i": i,
    }
    template = "reserve/reserve_details.html"

    return templates.TemplateResponse(template, context)


@router.post("/reserve-details/{id}")
async def reserve_details(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    form = await request.form()
    description = form["description"]
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
        reserve_period=reserve_period,
        rrf_us_id=current_user.id,
        rrf_tm_id=id,
        created_at=datetime.now(),
    )
    db.execute(query)
    db.commit()
    # ..
    return responses.RedirectResponse(
        f"/item-detail/{id}",
        status_code=302,
    )


@router.get("/list-reserve")
async def list_reserve(
    request: Request,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    rrf_us_id = current_user.id
    obj_list = await views.rrf_list(rrf_us_id, db)

    return templates.TemplateResponse(
        "reserve/list.html", {"request": request, "obj_list": obj_list}
    )


@router.get("/details-reserve/{id}")
async def details_reserve(
    request: Request,
    id: int,
    current_user: Annotated[EmailStr, Depends(get_active_user)],
    db: Session = Depends(get_db),
):
    rrf_us_id = current_user.id
    obj = await views.rrf_details(id, rrf_us_id, db)

    return templates.TemplateResponse(
        "reserve/details.html", {"request": request, "obj": obj}
    )
