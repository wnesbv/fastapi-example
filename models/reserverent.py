
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, String, Text, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.storage_config import Base


class ReserveRentFor(Base):
    __tablename__ = "reserverentfor_i"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    time_end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reserve_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    modified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # ...
    rrf_us_id: Mapped[int] = mapped_column(
        ForeignKey("user_us.id", ondelete="CASCADE"), nullable=False
    )
    rrf_tm_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    rrf_us: Mapped["User"] = relationship(back_populates="us_rrf")
    rrf_tm: Mapped["Item"] = relationship(back_populates="tm_rrf")

    def __str__(self):
        return self.id
