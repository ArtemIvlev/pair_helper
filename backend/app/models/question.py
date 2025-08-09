from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Question(Base):
    """Модель вопросов для пар из админки"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False, index=True)
    text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_answers = relationship("UserAnswer", back_populates="question")

    def __repr__(self):
        return f"<Question(id={self.id}, number={self.number}, category='{self.category}')>"


class UserAnswer(Base):
    """Ответы пользователей на вопросы"""
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Уникальность: один пользователь может ответить на вопрос только один раз
    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='unique_user_question'),)

    # Relationships
    user = relationship("User", back_populates="question_answers")
    question = relationship("Question", back_populates="user_answers")

    def __repr__(self):
        return f"<UserAnswer(id={self.id}, user_id={self.user_id}, question_id={self.question_id})>"


class UserQuestionStatus(Base):
    """Статус вопросов для пользователей в парах"""
    __tablename__ = "user_question_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    is_answered = Column(Integer, default=0)  # 0 - не отвечен, 1 - отвечен
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Уникальность: один статус на пользователя/пару/вопрос
    __table_args__ = (UniqueConstraint('user_id', 'pair_id', 'question_id', name='unique_user_pair_question'),)

    # Relationships
    user = relationship("User")
    pair = relationship("Pair")
    question = relationship("Question")

    def __repr__(self):
        return f"<UserQuestionStatus(user_id={self.user_id}, pair_id={self.pair_id}, question_id={self.question_id}, answered={self.is_answered})>"


class PairDailyQuestion(Base):
    """Назначенный на сегодня вопрос для пары (один на день)"""
    __tablename__ = "pair_daily_questions"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    date = Column(Date, nullable=False)  # Дата по UTC для уникальности в сутки
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('pair_id', 'date', name='unique_pair_per_day'),
    )

    pair = relationship("Pair")
    question = relationship("Question")

    def __repr__(self):
        return f"<PairDailyQuestion(pair_id={self.pair_id}, question_id={self.question_id}, date={self.date})>"

