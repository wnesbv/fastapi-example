
import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, true
from sqlalchemy.future import select

from starlette.responses import RedirectResponse

from config.settings import settings
from config.storage_config import async_session

from models.models import User, Privileged

from options_select.opt import left_right_first


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES


async def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key


# ...
async def get_token_privileged(request):
    if request.cookies.get("privileged"):
        token = request.cookies.get("privileged")
        if token:
            payload = jwt.decode(token, key, algorithm)
            prv_key = payload["prv_key"]
            return prv_key


async def get_privileged(request, session):
    token = await get_token_privileged(request)
    result = await left_right_first(session, Privileged, Privileged.prv_key, token)
    return result


async def get_privileged_user(request, session):
    while True:
        prv = await get_privileged(request, session)
        if not prv:
            break
        stmt = await session.execute(
            select(User).where(and_(User.id == prv.prv_in, User.privileged, true()))
        )
        result = stmt.scalars().first()
        return result


def privileged():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *a, **ka):
            async with async_session() as session:
                user = await get_privileged_user(request, session)
                if user:
                    return await func(request, *a, **ka)
            return RedirectResponse("/privileged/login")
        return wrapper
    return decorator
# ...


async def id_and_owner_prv(request, session, model, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(model).where(
            and_(
                model.id == id,
                model.owner == prv.id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def get_owner_prv(request, session, model):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(model).where(model.owner == prv.id)
    )
    result = stmt.scalars().all()
    return result


async def owner_prv(session, model, prv):
    stmt = await session.execute(
        select(model).where(model.owner == prv.id)
    )
    result = stmt.scalars().all()
    return result
