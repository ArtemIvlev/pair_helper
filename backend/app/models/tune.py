from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PairDailyTuneQuestion(Base):
    """Назначенный на сегодня вопрос для пары (Сонастройка). Один вопрос в день на пару.
    В отличие от обычного daily-question, этот сценарий предполагает 4 ответа:
    - пользователь о себе
    - пользователь о партнере
    - партнер о себе
    - партнер о пользователе
    """
    __tablename__ = "pair_daily_tune_questions"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("tune_quiz_questions.id"), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('pair_id', 'date', name='unique_pair_tune_per_day'),
    )

    pair = relationship("Pair")
    question = relationship("Question")

    def __repr__(self) -> str:
        return f"<PairDailyTuneQuestion(pair_id={self.pair_id}, question_id={self.question_id}, date={self.date})>"


class TuneAnswer(Base):
    """Ответ в режиме Сонастройки.
    author_user_id — кто отвечает
    subject_user_id — о ком ответ (сам автор или его партнер)
    """
    __tablename__ = "tune_answers"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("tune_quiz_questions.id"), nullable=False)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    selected_option = Column(Integer, nullable=True)  # 0..3 для MCQ; null для текстовых
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('pair_id', 'question_id', 'author_user_id', 'subject_user_id', name='unique_tune_answer_per_subject'),
    )

    pair = relationship("Pair")
    question = relationship("Question")

    def __repr__(self) -> str:
        return (
            f"<TuneAnswer(pair_id={self.pair_id}, q={self.question_id}, author={self.author_user_id}, "
            f"subject={self.subject_user_id})>"
        )


class TuneQuestionType(str, enum.Enum):
    TEXT = "text"
    MCQ = "mcq"


class TuneQuizQuestion(Base):
    """Банк вопросов для Сонастройки: поддерживает текстовые и MCQ с 4 вариантами."""
    __tablename__ = "tune_quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=True, index=True)
    # Универсальный текст (для совместимости), предпочтительнее использовать отдельные поля ниже
    text = Column(Text, nullable=True)
    # Раздельные формулировки
    text_about_partner = Column(Text, nullable=True)
    text_about_self = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    # Храним тип как строку для совместимости с админкой (значения: 'mcq'|'text')
    question_type = Column(String, default="mcq", nullable=False)
    option1 = Column(String, nullable=True)
    option2 = Column(String, nullable=True)
    option3 = Column(String, nullable=True)
    option4 = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<TuneQuizQuestion(id={self.id}, type={self.question_type}, category='{self.category}')>"


