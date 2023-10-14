
from datetime import datetime

from pydantic import BaseModel


class ReserveAdd(BaseModel):
    time_start: datetime
    time_end: datetime


class ReserveList(BaseModel):
    id: int
    description: str
    time_start: datetime
    time_end: datetime
    reserve_time: datetime | None = None
    created_at: datetime
    modified_at: datetime | None = None
    rrf_us_id: int
    rrf_tm_id: int

    class Config:
        from_attributes = True


class Reserve(BaseModel):
    id: int
    description: str
    time_start: datetime
    time_end: datetime
    reserve_time: datetime
    created_at: datetime
    modified_at: datetime
    rrf_us_id: int
    rrf_tm_id: int
    rrf_us: list["IUser"] = []
    rrf_tm: list["Item"] = []

    class Config:
        from_attributes = True


from user.schemas import IUser
from item.schemas import Item


ReserveList.update_forward_refs()
Reserve.update_forward_refs()
