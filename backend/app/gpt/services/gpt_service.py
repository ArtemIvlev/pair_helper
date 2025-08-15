import asyncio
import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.gpt_task import GPTTask, TaskStatus, TaskType
from ..schemas.gpt_schemas import AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)


class AnthropicService:
    """Сервис для работы с Anthropic API"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"
        
    async def analyze_text(self, prompt: str, system_prompt: str = None) -> str:
        """Анализ текста через Anthropic API"""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
            
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system_prompt:
            data["system"] = system_prompt
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result["content"][0]["text"]
                
            except Exception as e:
                logger.error(f"Anthropic API error: {e}")
                raise
    
    async def batch_analyze(self, prompts: List[str], system_prompt: str = None) -> List[str]:
        """Пакетный анализ текстов"""
        tasks = [self.analyze_text(prompt, system_prompt) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=True)


class InternalAPIService:
    """Сервис для вызова внутренних API"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        
    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Получение данных пользователя"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/{user_id}")
            response.raise_for_status()
            return response.json()
    
    async def get_pair_data(self, pair_id: int) -> Dict[str, Any]:
        """Получение данных пары"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/pairs/{pair_id}")
            response.raise_for_status()
            return response.json()
    
    async def get_mood_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Получение истории настроений"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/mood/history?user_id={user_id}&days={days}")
            response.raise_for_status()
            return response.json()
    
    async def get_question_answers(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение ответов на вопросы"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/questions/answers?user_id={user_id}&limit={limit}")
            response.raise_for_status()
            return response.json()


class GPTService:
    """Основной сервис для работы с GPT задачами"""
    
    def __init__(self):
        self.anthropic = AnthropicService()
        self.internal_api = InternalAPIService()
        
    async def create_task(self, task_type: TaskType, input_data: Dict[str, Any], 
                         user_id: Optional[int] = None, pair_id: Optional[int] = None) -> GPTTask:
        """Создание новой GPT задачи"""
        db = SessionLocal()
        try:
            task = GPTTask(
                task_type=task_type,
                input_data=input_data,
                user_id=user_id,
                pair_id=pair_id,
                status=TaskStatus.PENDING
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()
    
    async def process_task(self, task_id: int) -> AnalysisResponse:
        """Обработка GPT задачи"""
        db = SessionLocal()
        try:
            task = db.query(GPTTask).filter(GPTTask.id == task_id).first()
            if not task:
                return AnalysisResponse(success=False, error="Task not found")
            
            # Обновляем статус
            task.status = TaskStatus.PROCESSING
            task.started_at = datetime.utcnow()
            db.commit()
            
            start_time = datetime.utcnow()
            
            try:
                # Обрабатываем задачу в зависимости от типа
                if task.task_type == TaskType.RELATIONSHIP_ANALYSIS:
                    result = await self._analyze_relationship(task, db)
                elif task.task_type == TaskType.MOOD_ANALYSIS:
                    result = await self._analyze_mood(task, db)
                elif task.task_type == TaskType.QUESTION_GENERATION:
                    result = await self._generate_questions(task, db)
                elif task.task_type == TaskType.FEEDBACK_ANALYSIS:
                    result = await self._analyze_feedback(task, db)
                else:
                    result = await self._custom_analysis(task, db)
                
                # Обновляем результат
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.utcnow()
                db.commit()
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return AnalysisResponse(
                    success=True,
                    result=result,
                    task_id=task.id,
                    processing_time=processing_time
                )
                
            except Exception as e:
                # Обрабатываем ошибку
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.utcnow()
                db.commit()
                
                logger.error(f"Task {task_id} failed: {e}")
                return AnalysisResponse(
                    success=False,
                    error=str(e),
                    task_id=task.id
                )
                
        finally:
            db.close()
    
    async def _analyze_relationship(self, task: GPTTask, db: Session) -> str:
        """Анализ отношений пары"""
        if not task.pair_id:
            raise ValueError("Pair ID required for relationship analysis")
        
        # Получаем данные пары
        pair_data = await self.internal_api.get_pair_data(task.pair_id)
        task.internal_api_calls += 1
        
        # Получаем данные пользователей
        user1_data = await self.internal_api.get_user_data(pair_data["user1_id"])
        user2_data = await self.internal_api.get_user_data(pair_data["user2_id"])
        task.internal_api_calls += 2
        
        # Получаем историю настроений
        user1_moods = await self.internal_api.get_mood_history(user1_data["id"])
        user2_moods = await self.internal_api.get_mood_history(user2_data["id"])
        task.internal_api_calls += 2
        
        # Формируем промпт для анализа
        prompt = f"""
        Проанализируй отношения пары на основе следующих данных:
        
        Пользователь 1: {user1_data['first_name']} {user1_data.get('last_name', '')}
        Пользователь 2: {user2_data['first_name']} {user2_data.get('last_name', '')}
        
        История настроений пользователя 1: {user1_moods}
        История настроений пользователя 2: {user2_moods}
        
        Дополнительные данные: {task.input_data}
        
        Предоставь анализ в формате:
        1. Общая оценка отношений
        2. Сильные стороны
        3. Области для улучшения
        4. Рекомендации
        """
        
        system_prompt = "Ты эксперт по отношениям. Анализируй данные объективно и давай конструктивные рекомендации."
        
        # Вызываем Anthropic API
        result = await self.anthropic.analyze_text(prompt, system_prompt)
        task.anthropic_calls += 1
        
        return result
    
    async def _analyze_mood(self, task: GPTTask, db: Session) -> str:
        """Анализ настроения пользователя"""
        if not task.user_id:
            raise ValueError("User ID required for mood analysis")
        
        # Получаем историю настроений
        moods = await self.internal_api.get_mood_history(task.user_id)
        task.internal_api_calls += 1
        
        prompt = f"""
        Проанализируй настроение пользователя на основе истории:
        
        История настроений: {moods}
        Дополнительные данные: {task.input_data}
        
        Предоставь анализ:
        1. Тренды настроения
        2. Возможные причины изменений
        3. Рекомендации для улучшения
        """
        
        system_prompt = "Ты психолог-аналитик. Анализируй настроения и давай полезные рекомендации."
        
        result = await self.anthropic.analyze_text(prompt, system_prompt)
        task.anthropic_calls += 1
        
        return result
    
    async def _generate_questions(self, task: GPTTask, db: Session) -> str:
        """Генерация вопросов для пары"""
        prompt = f"""
        Сгенерируй интересные вопросы для пары на основе данных:
        
        Данные: {task.input_data}
        
        Создай 10-15 вопросов разных типов:
        - Вопросы о будущем
        - Вопросы о прошлом
        - Вопросы о ценностях
        - Вопросы о мечтах
        - Вопросы о повседневной жизни
        """
        
        system_prompt = "Ты эксперт по отношениям. Создавай глубокие, интересные вопросы для пар."
        
        result = await self.anthropic.analyze_text(prompt, system_prompt)
        task.anthropic_calls += 1
        
        return result
    
    async def _analyze_feedback(self, task: GPTTask, db: Session) -> str:
        """Анализ обратной связи"""
        prompt = f"""
        Проанализируй обратную связь пользователей:
        
        Данные обратной связи: {task.input_data}
        
        Предоставь анализ:
        1. Основные темы и проблемы
        2. Положительные аспекты
        3. Области для улучшения
        4. Приоритетные задачи
        """
        
        system_prompt = "Ты аналитик обратной связи. Выделяй ключевые инсайты и давай actionable рекомендации."
        
        result = await self.anthropic.analyze_text(prompt, system_prompt)
        task.anthropic_calls += 1
        
        return result
    
    async def _custom_analysis(self, task: GPTTask, db: Session) -> str:
        """Пользовательский анализ"""
        prompt = f"""
        Выполни пользовательский анализ:
        
        Тип анализа: {task.input_data.get('analysis_type', 'custom')}
        Данные: {task.input_data.get('data', {})}
        Опции: {task.input_data.get('options', {})}
        """
        
        result = await self.anthropic.analyze_text(prompt)
        task.anthropic_calls += 1
        
        return result
    
    async def batch_process(self, requests: List[AnalysisRequest]) -> List[AnalysisResponse]:
        """Пакетная обработка запросов"""
        results = []
        
        for request in requests:
            # Создаем задачу
            task_type = TaskType.CUSTOM_ANALYSIS
            if request.analysis_type == "relationship":
                task_type = TaskType.RELATIONSHIP_ANALYSIS
            elif request.analysis_type == "mood":
                task_type = TaskType.MOOD_ANALYSIS
            elif request.analysis_type == "questions":
                task_type = TaskType.QUESTION_GENERATION
            elif request.analysis_type == "feedback":
                task_type = TaskType.FEEDBACK_ANALYSIS
            
            task = await self.create_task(task_type, request.data)
            
            # Обрабатываем задачу
            result = await self.process_task(task.id)
            results.append(result)
        
        return results
