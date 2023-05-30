from datetime import datetime

import bcrypt

from sqlalchemy.orm import Session

from models.models import User, Item, Comment
from config.storage_config import Base, engine


def on_app_startup():
    Base.metadata.create_all(bind=engine)

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(("password").encode(), salt)

    with Session(engine) as session:
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
                    opinion_expressed="01 (one) item-opinion description",
                    cmt_user_id=1,
                    cmt_item_id=1,
                    created_at=datetime.now()
                ),
                Comment(
                    opinion_expressed="01 (two) item-opinion description",
                    cmt_user_id=2,
                    cmt_item_id=2,
                    created_at=datetime.now()
                ),
            ]
        )
        session.commit()
