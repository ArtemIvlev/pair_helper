from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from ..models.gpt_task import TaskStatus, TaskType


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskTypeEnum(str, Enum):
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    MOOD_ANALYSIS = "mood_analysis"
    QUESTION_GENERATION = "question_generation"
    FEEDBACK_ANALYSIS = "feedback_analysis"
    CUSTOM_ANALYSIS = "custom_analysis"


class GPTTaskCreate(BaseModel):
    task_type: TaskTypeEnum
    input_data: Dict[str, Any] = Field(..., description="Входные данные для анализа")
    user_id: Optional[int] = None
    pair_id: Optional[int] = None


class GPTTaskResponse(BaseModel):
    id: int
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    input_data: Dict[str, Any]
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[int] = None
    pair_id: Optional[int] = None
    anthropic_calls: int = 0
    internal_api_calls: int = 0

    class Config:
        from_attributes = True


class GPTTaskList(BaseModel):
    tasks: List[GPTTaskResponse]
    total: int
    page: int
    size: int


class AnalysisRequest(BaseModel):
    """Запрос на анализ данных"""
    data: Dict[str, Any] = Field(..., description="Данные для анализа")
    analysis_type: str = Field(..., description="Тип анализа")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные опции")


class AnalysisResponse(BaseModel):
    """Ответ с результатом анализа"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    task_id: Optional[int] = None
    processing_time: Optional[float] = None


class BatchAnalysisRequest(BaseModel):
    """Запрос на пакетный анализ"""
    tasks: List[AnalysisRequest] = Field(..., description="Список задач для анализа")
    priority: str = Field(default="normal", description="Приоритет обработки")


class BatchAnalysisResponse(BaseModel):
    """Ответ на пакетный анализ"""
    batch_id: str
    total_tasks: int
    submitted_tasks: int
    estimated_time: Optional[float] = None
    message: str
