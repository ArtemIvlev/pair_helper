from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.pair import PairStatus, InviteStatus


class PairBase(BaseModel):
    user1_id: int
    user2_id: int
    status: PairStatus = PairStatus.ACTIVE


class PairCreate(PairBase):
    pass


class Pair(PairBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PairInviteBase(BaseModel):
    code: str
    owner_user_id: int
    status: InviteStatus = InviteStatus.PENDING
    expires_at: datetime


class PairInviteCreate(BaseModel):
    owner_user_id: int


class PairInvite(PairInviteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
