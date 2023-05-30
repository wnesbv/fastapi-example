from __future__ import annotations
from typing import List

from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from config.storage_config import Base


class User(Base):
    __tablename__ = "user_u"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name = Column(String, nullable=True)
    email: Mapped[str] = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    # ...
    user_item: Mapped[List["Item"]] = relationship(back_populates="item_user")
    user_cmt: Mapped[List["Comment"]] = relationship(back_populates="cmt_user")
    user_like: Mapped[List["Like"]] = relationship(back_populates="like_user")
    user_dislike: Mapped[List["Dislike"]] = relationship(back_populates="dislike_user")

    def __str__(self):
        return str(self.name)


class Item(Base):
    __tablename__ = "item_i"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    # ...
    owner_item_id: Mapped[int] = mapped_column(
        ForeignKey("user_u.id", ondelete="CASCADE")
    )
    # ...
    item_user: Mapped["User"] = relationship(back_populates="user_item")
    item_cmt: Mapped["Comment"] = relationship(back_populates="cmt_item")
    item_like: Mapped["Like"] = relationship(back_populates="like_item")
    item_dislike: Mapped["Dislike"] = relationship(back_populates="dislike_item")

    def __str__(self):
        return self.id


class Comment(Base):
    __tablename__ = "comment_c"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    opinion_expressed = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    # ...
    cmt_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_u.id", ondelete="CASCADE")
    )
    cmt_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_i.id", ondelete="CASCADE")
    )
    # ...
    cmt_user: Mapped["User"] = relationship(back_populates="user_cmt")
    cmt_item: Mapped["Item"] = relationship(back_populates="item_cmt")

    def __str__(self):
        return self.id


# ...


class Like(Base):
    __tablename__ = "like_l"

    upvote = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)
    # ...
    like_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_u.id", ondelete="CASCADE"), primary_key=True
    )
    like_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_i.id", ondelete="CASCADE"), primary_key=True
    )
    # ..
    like_user: Mapped["User"] = relationship(back_populates="user_like")
    like_item: Mapped["Item"] = relationship(back_populates="item_like")

    def __str__(self):
        return str(self.like_user_id)


class Dislike(Base):
    __tablename__ = "dislike_d"

    downvote = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=True)
    # ...
    dislike_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_u.id", ondelete="CASCADE"), primary_key=True
    )
    dislike_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_i.id", ondelete="CASCADE"), primary_key=True
    )
    # ...
    dislike_user: Mapped["User"] = relationship(back_populates="user_dislike")
    dislike_item: Mapped["Item"] = relationship(back_populates="item_dislike")

    def __str__(self):
        return str(self.dislike_user_id)
