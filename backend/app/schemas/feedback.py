from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.feedback import FeedbackType, FeedbackStatus


class FeedbackBase(BaseModel):
    feedback_type: FeedbackType
    subject: str
    message: str


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    status: Optional[FeedbackStatus] = None
    admin_response: Optional[str] = None


class UserInfo(BaseModel):
    first_name: str
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


class Feedback(FeedbackBase):
    id: int
    user_id: int
    status: FeedbackStatus
    admin_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: UserInfo

    class Config:
        from_attributes = True


class FeedbackList(BaseModel):
    feedback: list[Feedback]
    total: int
    page: int
    per_page: int
