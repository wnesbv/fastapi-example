from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from models import models
from item.views import search_item
from config.dependency import get_session
from options_select.opt import in_all


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(
    request: Request, session: AsyncSession = Depends(get_session), msg: str = None
):
    obj_list = await in_all(session, models.User)

    return templates.TemplateResponse(
        "index.html", {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/search/")
async def autocomplete(
    request: Request,
    query: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    obj_list = await search_item(query, session=session)

    return templates.TemplateResponse(
        "components/search.html", {"request": request, "obj_list": obj_list}
    )
