from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class DailyQuestion(Base):
    __tablename__ = "daily_questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    answers = relationship("Answer", back_populates="question")

    def __repr__(self):
        return f"<DailyQuestion(id={self.id}, text='{self.text[:50]}...')>"


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("daily_questions.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="answers")
    question = relationship("DailyQuestion", back_populates="answers")

    def __repr__(self):
        return f"<Answer(id={self.id}, user_id={self.user_id}, question_id={self.question_id})>"
