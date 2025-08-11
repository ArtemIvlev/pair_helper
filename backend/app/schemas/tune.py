from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TuneQuestionType(str):
    TEXT = "text"
    MCQ = "mcq"


class TuneQuestionResponse(BaseModel):
    id: int
    number: int
    text: str
    category: str
    question_type: str = "mcq"
    option1: str | None = None
    option2: str | None = None
    option3: str | None = None
    option4: str | None = None
    # Раздельные формулировки
    text_about_partner: str | None = None
    text_about_self: str | None = None


    class Config:
        from_attributes = True


class TuneAnswerCreate(BaseModel):
    question_id: int = Field(..., description="ID вопроса")
    about: str = Field(..., pattern="^(me|partner)$", description="О ком ответ: me|partner")
    answer_text: str | None = Field(None, description="Текст ответа для текстового вопроса")
    selected_option: int | None = Field(None, ge=0, le=3, description="Индекс выбранного варианта для MCQ (0..3)")


class TuneAnswerItem(BaseModel):
    id: int
    author_user_id: int
    subject_user_id: int
    answer_text: str
    created_at: datetime
    is_me: bool = False
    is_about_me: bool = False

    class Config:
        from_attributes = True


class TuneAnswersStatus(BaseModel):
    about_me: Optional[int] = None  # Значение ответа (0-3)
    about_partner: Optional[int] = None  # Значение ответа (0-3)

class TunePartnerAnswersStatus(BaseModel):
    about_himself: Optional[int] = None  # Значение ответа (0-3)
    about_me: Optional[int] = None  # Значение ответа (0-3)

class TunePairAnswersResponse(BaseModel):
    question: TuneQuestionResponse
    partner_name: str = "Партнер"
    me: Optional[TuneAnswersStatus] = None
    partner: Optional[TunePartnerAnswersStatus] = None


class TuneQuizQuestionBase(BaseModel):
    text: str | None = None
    text_about_partner: str | None = None
    text_about_self: str | None = None
    category: str
    question_type: str = Field("text", pattern="^(text|mcq)$")
    option1: str | None = None
    option2: str | None = None
    option3: str | None = None
    option4: str | None = None


class TuneQuizQuestionCreate(TuneQuizQuestionBase):
    number: int | None = None


class TuneQuizQuestion(TuneQuizQuestionBase):
    id: int
    number: int | None = None

    class Config:
        from_attributes = True


