from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.models.pair import PairStatus, InviteStatus
from app.schemas.user import User


class PairBase(BaseModel):
    user1_id: int
    user2_id: int
    status: PairStatus = PairStatus.ACTIVE


class PairCreate(PairBase):
    pass


class Pair(PairBase):
    id: int
    created_at: datetime
    user1: Optional[User] = None
    user2: Optional[User] = None

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


class PairActivityItem(BaseModel):
    """Элемент активности пары"""
    date: str
    type: str  # mood, appreciation, ritual, calendar, emotion_note, question, tune
    title: str
    description: str
    user_name: str
    timestamp: datetime

    class Config:
        from_attributes = True


class PairWeeklyActivity(BaseModel):
    """Активность пары за неделю в человекочитаемом формате"""
    pair_id: int
    user1_name: str
    user2_name: str
    week_start: str
    week_end: str
    activities: List[PairActivityItem]
    summary: str

    class Config:
        from_attributes = True
