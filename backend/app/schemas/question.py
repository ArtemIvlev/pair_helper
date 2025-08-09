from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    """Схема для ответа с вопросом"""
    id: int
    number: int
    text: str
    category: str
    partner_answered: bool = False
    user_answered: bool = False

    class Config:
        from_attributes = True


class UserAnswerCreate(BaseModel):
    """Схема для создания ответа пользователя"""
    question_id: int = Field(..., description="ID вопроса")
    answer_text: str = Field(..., min_length=1, max_length=2000, description="Текст ответа")


class UserAnswerResponse(BaseModel):
    """Схема для ответа с пользовательским ответом"""
    id: int
    question_id: int
    answer_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionStatusResponse(BaseModel):
    """Схема для статуса вопроса в паре"""
    question: QuestionResponse
    user_answered: bool
    partner_answered: bool
    can_view_answers: bool


class PairAnswersResponse(BaseModel):
    """Схема для ответов пары на вопрос"""
    question: QuestionResponse
    user_answer: Optional[UserAnswerResponse] = None
    partner_answer: Optional[UserAnswerResponse] = None
    partner_name: str = "Партнер"


class QuestionsStatsResponse(BaseModel):
    """Схема для статистики по вопросам"""
    total_questions: int
    user_answered: int
    partner_answered: int
    both_answered: int
    completion_percentage: float

