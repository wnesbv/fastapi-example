from datetime import datetime, timedelta

import bcrypt, time, string, secrets

from passlib.hash import pbkdf2_sha1

from models.reserverent import ReserveRentFor
from models.models import User, Privileged, Item, Comment, Like, Dislike
from .storage_config import Base, engine, async_session


def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key


async def on_app_startup() -> None:
    async with engine.begin() as conn:
        # ..
        start = time.time()
        print(" start..")
        # ..
        await conn.run_sync(Base.metadata.create_all)
        # ..
        end = time.time()
        print(" end..", end - start)

    async with async_session() as session:
        async with session.begin():
            # ..
            passlib_hash = pbkdf2_sha1.hash("password")
            # ..
            # ..
            salt = bcrypt.gensalt()
            bcrypt_hash = bcrypt.hashpw(("password").encode(), salt)
            # ..
            start = time.time()
            print(" start all..")
            # ..
            session.add_all(
                [
                    User(
                        name="one",
                        email="one@example.com",
                        password=passlib_hash,
                        privileged=True,
                        is_admin=True,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
                    ),
                    User(
                        name="two",
                        email="two@example.com",
                        password=bcrypt_hash,
                        privileged=False,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
                    ),
                    Privileged(
                        prv_key=get_random_string(),
                        prv_in=1,
                    ),
                    Item(
                        title="item 01 one",
                        description="description",
                        owner_item_id=1,
                        created_at=datetime.now()
                    ),
                    Item(
                        title="item 02 two",
                        description="description 02 two",
                        owner_item_id=2,
                        created_at=datetime.now()
                    ),
                    Comment(
                        opinion_expressed="01 (one) opinion description",
                        cmt_user_id=1,
                        cmt_item_id=1,
                        created_at=datetime.now()
                    ),
                    Comment(
                        opinion_expressed="01 (two) opinion description",
                        cmt_user_id=2,
                        cmt_item_id=2,
                        created_at=datetime.now()
                    ),
                    Like(
                        upvote=True,
                        like_user_id=1,
                        like_item_id=1,
                        created_at=datetime.now()
                    ),
                    Dislike(
                        downvote=False,
                        dislike_user_id=2,
                        dislike_item_id=2,
                        created_at=datetime.now()
                    ),
                    Dislike(
                        downvote=False,
                        dislike_user_id=2,
                        dislike_item_id=1,
                        created_at=datetime.now()
                    ),
                    ReserveRentFor(
                        time_start=datetime.now(),
                        time_end=datetime.now() + timedelta(days=1),
                        reserve_time=datetime.now(),
                        rrf_us_id=1,
                        rrf_tm_id=1,
                    ),
                    ReserveRentFor(
                        time_start=datetime.now() + timedelta(days=2),
                        time_end=datetime.now() + timedelta(days=3),
                        reserve_time=datetime.now() + timedelta(days=1),
                        rrf_us_id=2,
                        rrf_tm_id=2,
                    ),
                ]
            )
            await session.flush()
        await session.commit()
        end = time.time()
        print(" end all..", end - start)
    await engine.dispose()
