from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.config import settings
from ..services.gpt_service import GPTService
from ..schemas.gpt_schemas import (
    GPTTaskCreate, GPTTaskResponse, GPTTaskList,
    AnalysisRequest, AnalysisResponse,
    BatchAnalysisRequest, BatchAnalysisResponse
)
from app.models.gpt_task import TaskType, TaskStatus

router = APIRouter()


def get_gpt_service() -> GPTService:
    return GPTService()


@router.post("/tasks", response_model=GPTTaskResponse)
async def create_task(
    task: GPTTaskCreate,
    db: Session = Depends(get_db),
    gpt_service: GPTService = Depends(get_gpt_service)
):
    """Создание новой GPT задачи"""
    try:
        task_obj = await gpt_service.create_task(
            task_type=TaskType(task.task_type.value),
            input_data=task.input_data,
            user_id=task.user_id,
            pair_id=task.pair_id
        )
        return GPTTaskResponse.from_orm(task_obj)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}", response_model=GPTTaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Получение информации о задаче"""
    from app.models.gpt_task import GPTTask
    
    task = db.query(GPTTask).filter(GPTTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return GPTTaskResponse.from_orm(task)


@router.get("/tasks", response_model=GPTTaskList)
async def list_tasks(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Список задач с фильтрацией"""
    from app.models.gpt_task import GPTTask
    
    query = db.query(GPTTask)
    
    if status:
        query = query.filter(GPTTask.status == TaskStatus(status))
    
    if task_type:
        query = query.filter(GPTTask.task_type == TaskType(task_type))
    
    total = query.count()
    tasks = query.offset((page - 1) * size).limit(size).all()
    
    return GPTTaskList(
        tasks=[GPTTaskResponse.from_orm(task) for task in tasks],
        total=total,
        page=page,
        size=size
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    gpt_service: GPTService = Depends(get_gpt_service)
):
    """Анализ данных (создает задачу и запускает обработку в фоне)"""
    try:
        # Определяем тип задачи
        task_type = TaskType.CUSTOM_ANALYSIS
        if request.analysis_type == "relationship":
            task_type = TaskType.RELATIONSHIP_ANALYSIS
        elif request.analysis_type == "mood":
            task_type = TaskType.MOOD_ANALYSIS
        elif request.analysis_type == "questions":
            task_type = TaskType.QUESTION_GENERATION
        elif request.analysis_type == "feedback":
            task_type = TaskType.FEEDBACK_ANALYSIS
        
        # Создаем задачу
        task = await gpt_service.create_task(
            task_type=task_type,
            input_data=request.data
        )
        
        # Запускаем обработку в фоне
        background_tasks.add_task(gpt_service.process_task, task.id)
        
        return AnalysisResponse(
            success=True,
            task_id=task.id,
            message="Task created and processing started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze/sync", response_model=AnalysisResponse)
async def analyze_data_sync(
    request: AnalysisRequest,
    gpt_service: GPTService = Depends(get_gpt_service)
):
    """Синхронный анализ данных (создает задачу и сразу обрабатывает)"""
    try:
        # Определяем тип задачи
        task_type = TaskType.CUSTOM_ANALYSIS
        if request.analysis_type == "relationship":
            task_type = TaskType.RELATIONSHIP_ANALYSIS
        elif request.analysis_type == "mood":
            task_type = TaskType.MOOD_ANALYSIS
        elif request.analysis_type == "questions":
            task_type = TaskType.QUESTION_GENERATION
        elif request.analysis_type == "feedback":
            task_type = TaskType.FEEDBACK_ANALYSIS
        
        # Создаем задачу
        task = await gpt_service.create_task(
            task_type=task_type,
            input_data=request.data
        )
        
        # Сразу обрабатываем
        result = await gpt_service.process_task(task.id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=BatchAnalysisResponse)
async def batch_analyze(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    gpt_service: GPTService = Depends(get_gpt_service)
):
    """Пакетный анализ данных"""
    try:
        # Создаем задачи для всех запросов
        tasks = []
        for analysis_request in request.tasks:
            task_type = TaskType.CUSTOM_ANALYSIS
            if analysis_request.analysis_type == "relationship":
                task_type = TaskType.RELATIONSHIP_ANALYSIS
            elif analysis_request.analysis_type == "mood":
                task_type = TaskType.MOOD_ANALYSIS
            elif analysis_request.analysis_type == "questions":
                task_type = TaskType.QUESTION_GENERATION
            elif analysis_request.analysis_type == "feedback":
                task_type = TaskType.FEEDBACK_ANALYSIS
            
            task = await gpt_service.create_task(
                task_type=task_type,
                input_data=analysis_request.data
            )
            tasks.append(task)
        
        # Запускаем обработку всех задач в фоне
        for task in tasks:
            background_tasks.add_task(gpt_service.process_task, task.id)
        
        return BatchAnalysisResponse(
            batch_id=f"batch_{tasks[0].id}_{tasks[-1].id}",
            total_tasks=len(tasks),
            submitted_tasks=len(tasks),
            estimated_time=len(tasks) * 30,  # Примерно 30 секунд на задачу
            message=f"Created {len(tasks)} tasks for batch processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/{task_id}/process")
async def process_task(
    task_id: int,
    gpt_service: GPTService = Depends(get_gpt_service)
):
    """Запуск обработки конкретной задачи"""
    try:
        result = await gpt_service.process_task(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Удаление задачи"""
    from app.models.gpt_task import GPTTask
    
    task = db.query(GPTTask).filter(GPTTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.get("/health")
async def health_check():
    """Проверка здоровья GPT модуля"""
    return {
        "status": "healthy",
        "module": "gpt",
        "anthropic_configured": bool(settings.ANTHROPIC_API_KEY)
    }
