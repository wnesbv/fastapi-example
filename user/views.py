
import jwt, functools
from fastapi import Request, Depends, HTTPException, status, responses

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.storage_config import engine, async_session

from user import schemas
from models import models

from account.auth import auth
from account.views import get_user_by_id, get_user_by_email
from config.dependency import get_session


# ..
async def get_access_id(request: Request):
    if request.cookies.get("access_token"):
        token = request.cookies.get("access_token")
        if token:
            payload = await auth.decode_token_all(token)
            user_id = payload["user_id"]
            return user_id


async def id_access(request: Request, session: AsyncSession = Depends(get_session)):
    user_id = await get_access_id(request)
    result = await get_user_by_id(user_id, session)
    return result


async def access_user_id(request: Request, session: AsyncSession = Depends(get_session)):
    while True:
        user = await id_access(request, session)
        if not user:
            break
        result = await get_user_by_id(user.id, session)
        return result
# ..


def access_token():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *a, **ka):
            async with async_session() as session:
                user = await access_user_id(request, session)
            await engine.dispose()
            if user:
                return await func(request, *a, **ka)
            return responses.RedirectResponse("/login")
        return wrapper
    return decorator


# ..
async def get_access_email(request: Request):
    if request.cookies.get("access_token"):
        token = request.cookies.get("access_token")
        if token:
            payload = await auth.decode_token(token)
            email = payload["email"]
            return email


async def get_access(request: Request, session: AsyncSession = Depends(get_session)):
    email = await get_access_email(request)
    result = await get_user_by_email(email, session)
    return result


async def access_email_user(request: Request, session: AsyncSession = Depends(get_session)):
    while True:
        user = await get_access(request, session)
        if not user:
            break
        result = await get_user_by_email(user.email, session)
        return result
# ..


def get_token(
    request: Request,
):
    if not request.cookies.get("access_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no authorization, log in..!",
        )
    token = request.cookies.get("access_token")
    return token


async def get_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(get_token),
):

    email = await auth.decode_token(token)
    user = await get_user_by_email(email, session)
    if not user:
        raise HTTPException(401, "User doesn't exist")
    return user


def get_active_user(current_user: schemas.GetUser = Depends(get_user)):
    if not current_user.email_verified:
        raise HTTPException(401, "Электронная почта не подтверждена!")
    if not current_user.is_active:
        raise HTTPException(401, "Этот аккаунт не активен!")
    return current_user


async def get_user_id(
    session: AsyncSession,
    current_user: schemas.GetUser = Depends(get_user)
):
    stmt = await session.execute(
        select(models.User).where(models.User.id == current_user.id)
    )
    result = stmt.scalars().first()
    return result


# ...
async def update_user(
    id: int,
    password: str,
    obj_in: schemas.UserUpdate,
    session: AsyncSession,
):
    # ..
    obj_in.__dict__.update(password=password)
    # ..
    query = (
        sql_update(models.User)
        .where(models.User.id == id)
        .values(obj_in.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(query)
    await session.commit()

    return query


async def retreive_user(id: int, session: AsyncSession):
    stmt = await session.execute(
        select(models.User)
        .where(models.User.id == id)
    )
    result = stmt.scalars().first()
    return result


async def count_user_item(id: int, session: AsyncSession):
    stmt = await session.execute(
        select(models.Item)
        .where(models.Item.owner_item_id == id)
    )
    result = stmt.scalars().all()
    return result
