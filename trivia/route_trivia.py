
from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from user import schemas

from item.views import search_item
from user.views import get_active_user, list_user
from config.dependency import get_db


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/search/")
def autocomplete(
    request: Request,
    query: str | None = None,
    db: Session = Depends(get_db)
):

    obj_list = search_item(query, db=db)

    return templates.TemplateResponse(
        "components/search.html",
        {"request": request, "obj_list": obj_list}
    )


# ...

@router.get("/")
async def home(
    request: Request,
    db: Session = Depends(get_db),
    msg: str = None
):

    obj_list = list_user(db=db)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "obj_list": obj_list, "msg": msg}
    )


@router.get("/me/", response_model=schemas.User)
def get_user_profile(
    current_user: schemas.User = Depends(get_active_user)
):
    return current_user
