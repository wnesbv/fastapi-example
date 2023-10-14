from datetime import datetime, timedelta

import bcrypt, time

from models.reserverent import ReserveRentFor
from models.models import User, Item, Comment, Like, Dislike
from config.storage_config import Base, engine, async_session


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
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(("password").encode(), salt)
            # ..
            start = time.time()
            print(" start all..")
            # ..
            session.add_all(
                [
                    User(
                        name="one",
                        email="one@example.com",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
                    ),
                    User(
                        name="two",
                        email="two@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now()
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
