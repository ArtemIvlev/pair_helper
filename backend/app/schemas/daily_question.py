from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DailyQuestionBase(BaseModel):
    text: str
    is_active: bool = True


class DailyQuestion(DailyQuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerBase(BaseModel):
    question_id: int
    text: str


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    user_id: int
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True
