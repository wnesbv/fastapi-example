from __future__ import annotations

from sqlalchemy import Boolean, String, Text, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.storage_config import (
    Base,
    intpk,
    pictures,
    points,
    user_fk,
)


class User(Base):
    __tablename__ = "user_us"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    # ...
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # ...
    created_at: Mapped[points]
    modified_at: Mapped[points]

    # ...
    user_item: Mapped[list["Item"]] = relationship(
        back_populates="item_user", cascade="all, delete-orphan"
    )
    user_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_user", cascade="all, delete-orphan"
    )
    user_like: Mapped[list["Like"]] = relationship(
        back_populates="like_user",
    )
    user_dislike: Mapped[list["Dislike"]] = relationship(back_populates="dislike_user")

    us_rrf: Mapped[list["ReserveRentFor"]] = relationship(back_populates="rrf_us")

    def __str__(self):
        return str(self.name)


class Item(Base):
    __tablename__ = "item_tm"

    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner_item_id: Mapped[user_fk]
    # ...
    item_user: Mapped["User"] = relationship(back_populates="user_item")
    item_cmt: Mapped["Comment"] = relationship(
        back_populates="cmt_item", cascade="all, delete-orphan"
    )
    item_like: Mapped["Like"] = relationship(
        back_populates="like_item", cascade="all, delete-orphan"
    )
    item_dislike: Mapped["Dislike"] = relationship(
        back_populates="dislike_item", cascade="all, delete-orphan"
    )
    # ...
    tm_rrf: Mapped["ReserveRentFor"] = relationship(
        back_populates="rrf_tm", cascade="all, delete-orphan"
    )

    def __str__(self):
        return self.id


class Comment(Base):
    __tablename__ = "comment_cmt"

    id: Mapped[intpk]
    opinion_expressed: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    cmt_user_id: Mapped[user_fk]
    cmt_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    cmt_user: Mapped["User"] = relationship(back_populates="user_cmt")
    cmt_item: Mapped["Item"] = relationship(back_populates="item_cmt")

    def __str__(self):
        return self.id


# ...


class Like(Base):
    __tablename__ = "like_lk"

    upvote: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[points]
    # ...
    like_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_us.id", ondelete="CASCADE"), primary_key=True
    )
    like_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), primary_key=True
    )
    # ..
    like_user: Mapped["User"] = relationship(back_populates="user_like")
    like_item: Mapped["Item"] = relationship(back_populates="item_like")

    def __str__(self):
        return str(self.like_user_id)


class Dislike(Base):
    __tablename__ = "dislike_dlk"

    downvote: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[points]
    # ...
    dislike_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_us.id", ondelete="CASCADE"), primary_key=True
    )
    dislike_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), primary_key=True
    )
    # ...
    dislike_user: Mapped["User"] = relationship(back_populates="user_dislike")
    dislike_item: Mapped["Item"] = relationship(back_populates="item_dislike")

    def __str__(self):
        return str(self.dislike_user_id)
