
from __future__ import annotations

from sqlalchemy import Boolean, Column, String, Text, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.storage_config import Base


class ReserveRentFor(Base):
    __tablename__ = "reserverentfor_i"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description = Column(Text, nullable=True)
    time_start = Column(DateTime, nullable=True)
    time_end = Column(DateTime, nullable=True)
    reserve_time = Column(DateTime, nullable=True)
    reserve_period = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    modified_at = Column(DateTime, nullable=True)
    # ...
    rrf_us_id: Mapped[int] = mapped_column(
        ForeignKey("user_u.id", ondelete="CASCADE"), nullable=False
    )
    rrf_tm_id: Mapped[int] = mapped_column(
        ForeignKey("item_i.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    rrf_us: Mapped["User"] = relationship(back_populates="us_rrf")
    rrf_tm: Mapped["Item"] = relationship(back_populates="tm_rrf")

    def __str__(self):
        return self.id
