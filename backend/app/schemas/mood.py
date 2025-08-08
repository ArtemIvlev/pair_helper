from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MoodBase(BaseModel):
    mood_code: str  # joyful, calm, tired, anxious, sad, irritable, grateful
    note: Optional[str] = None


class MoodCreate(MoodBase):
    pass


class Mood(MoodBase):
    id: int
    user_id: int
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AppreciationBase(BaseModel):
    text: str


class AppreciationCreate(AppreciationBase):
    pass


class Appreciation(AppreciationBase):
    id: int
    user_id: int
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
