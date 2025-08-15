from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.core.database import Base


class TaskStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(PyEnum):
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    MOOD_ANALYSIS = "mood_analysis"
    QUESTION_GENERATION = "question_generation"
    FEEDBACK_ANALYSIS = "feedback_analysis"
    CUSTOM_ANALYSIS = "custom_analysis"


class GPTTask(Base):
    __tablename__ = "gpt_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Входные данные
    input_data = Column(JSON, nullable=False)
    
    # Результат
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связанные данные
    user_id = Column(Integer, nullable=True)  # Если задача связана с пользователем
    pair_id = Column(Integer, nullable=True)  # Если задача связана с парой
    
    # Внешние API вызовы
    anthropic_calls = Column(Integer, default=0)
    internal_api_calls = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<GPTTask(id={self.id}, type={self.task_type}, status={self.status})>"
