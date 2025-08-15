import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.scheduler import scheduler
from app.models.gpt_task import GPTTask, TaskStatus, TaskType
from ..services.gpt_service import GPTService

logger = logging.getLogger(__name__)


class GPTScheduler:
    """Планировщик для автоматического запуска GPT задач"""
    
    def __init__(self):
        self.gpt_service = GPTService()
        
    async def schedule_daily_analysis(self):
        """Планирование ежедневного анализа для всех активных пар"""
        logger.info("🚀 Запуск ежедневного GPT анализа...")
        
        db = SessionLocal()
        try:
            # Получаем все активные пары
            from app.models.pair import Pair
            active_pairs = db.query(Pair).filter(Pair.is_active == True).all()
            
            logger.info(f"Найдено {len(active_pairs)} активных пар для анализа")
            
            for pair in active_pairs:
                try:
                    # Создаем задачу анализа отношений
                    await self.gpt_service.create_task(
                        task_type=TaskType.RELATIONSHIP_ANALYSIS,
                        input_data={
                            "analysis_date": datetime.utcnow().isoformat(),
                            "pair_id": pair.id
                        },
                        pair_id=pair.id
                    )
                    
                    logger.info(f"Создана задача анализа для пары {pair.id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка создания задачи для пары {pair.id}: {e}")
            
            # Запускаем обработку задач в фоне
            await self._process_pending_tasks()
            
        except Exception as e:
            logger.error(f"Ошибка в ежедневном анализе: {e}")
        finally:
            db.close()
    
    async def schedule_weekly_feedback_analysis(self):
        """Планирование еженедельного анализа обратной связи"""
        logger.info("📊 Запуск еженедельного анализа обратной связи...")
        
        db = SessionLocal()
        try:
            # Получаем обратную связь за последнюю неделю
            from app.models.feedback import Feedback
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            recent_feedback = db.query(Feedback).filter(
                Feedback.created_at >= week_ago
            ).all()
            
            if recent_feedback:
                # Создаем задачу анализа обратной связи
                feedback_data = [
                    {
                        "id": f.id,
                        "text": f.text,
                        "rating": f.rating,
                        "created_at": f.created_at.isoformat()
                    }
                    for f in recent_feedback
                ]
                
                await self.gpt_service.create_task(
                    task_type=TaskType.FEEDBACK_ANALYSIS,
                    input_data={
                        "feedback_data": feedback_data,
                        "period": "weekly",
                        "total_feedback": len(feedback_data)
                    }
                )
                
                logger.info(f"Создана задача анализа {len(feedback_data)} отзывов")
            
        except Exception as e:
            logger.error(f"Ошибка в еженедельном анализе: {e}")
        finally:
            db.close()
    
    async def schedule_mood_trend_analysis(self):
        """Планирование анализа трендов настроений"""
        logger.info("😊 Запуск анализа трендов настроений...")
        
        db = SessionLocal()
        try:
            # Получаем всех активных пользователей
            from app.models.user import User
            active_users = db.query(User).filter(User.is_active == True).all()
            
            for user in active_users:
                try:
                    # Создаем задачу анализа настроения
                    await self.gpt_service.create_task(
                        task_type=TaskType.MOOD_ANALYSIS,
                        input_data={
                            "analysis_period": "monthly",
                            "user_id": user.id
                        },
                        user_id=user.id
                    )
                    
                    logger.info(f"Создана задача анализа настроения для пользователя {user.id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка создания задачи для пользователя {user.id}: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка в анализе настроений: {e}")
        finally:
            db.close()
    
    async def schedule_question_generation(self):
        """Планирование генерации новых вопросов"""
        logger.info("❓ Запуск генерации новых вопросов...")
        
        try:
            # Создаем задачу генерации вопросов
            await self.gpt_service.create_task(
                task_type=TaskType.QUESTION_GENERATION,
                input_data={
                    "generation_date": datetime.utcnow().isoformat(),
                    "question_types": ["relationship", "personal", "future", "values"],
                    "count": 20
                }
            )
            
            logger.info("Создана задача генерации вопросов")
            
        except Exception as e:
            logger.error(f"Ошибка в генерации вопросов: {e}")
    
    async def _process_pending_tasks(self):
        """Обработка ожидающих задач"""
        db = SessionLocal()
        try:
            # Получаем все ожидающие задачи
            pending_tasks = db.query(GPTTask).filter(
                GPTTask.status == TaskStatus.PENDING
            ).limit(10).all()  # Ограничиваем количество одновременно обрабатываемых задач
            
            logger.info(f"Найдено {len(pending_tasks)} ожидающих задач")
            
            for task in pending_tasks:
                try:
                    # Запускаем обработку в фоне
                    asyncio.create_task(self.gpt_service.process_task(task.id))
                    logger.info(f"Запущена обработка задачи {task.id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка запуска задачи {task.id}: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки ожидающих задач: {e}")
        finally:
            db.close()
    
    async def cleanup_old_tasks(self):
        """Очистка старых задач"""
        logger.info("🧹 Запуск очистки старых задач...")
        
        db = SessionLocal()
        try:
            # Удаляем задачи старше 30 дней
            month_ago = datetime.utcnow() - timedelta(days=30)
            
            old_tasks = db.query(GPTTask).filter(
                GPTTask.created_at < month_ago,
                GPTTask.status.in_([TaskStatus.COMPLETED, TaskStatus.FAILED])
            ).all()
            
            for task in old_tasks:
                db.delete(task)
            
            db.commit()
            logger.info(f"Удалено {len(old_tasks)} старых задач")
            
        except Exception as e:
            logger.error(f"Ошибка очистки задач: {e}")
            db.rollback()
        finally:
            db.close()


# Создаем экземпляр планировщика
gpt_scheduler = GPTScheduler()


# Регистрируем задачи в планировщике
def register_gpt_jobs():
    """Регистрация GPT задач в планировщике"""
    
    # Ежедневный анализ отношений (каждый день в 6:00)
    scheduler.scheduler.add_job(
        gpt_scheduler.schedule_daily_analysis,
        'cron',
        hour=6,
        minute=0,
        id='gpt_daily_analysis',
        name='Ежедневный GPT анализ отношений'
    )
    
    # Еженедельный анализ обратной связи (каждый понедельник в 8:00)
    scheduler.scheduler.add_job(
        gpt_scheduler.schedule_weekly_feedback_analysis,
        'cron',
        day_of_week='mon',
        hour=8,
        minute=0,
        id='gpt_weekly_feedback',
        name='Еженедельный анализ обратной связи'
    )
    
    # Анализ трендов настроений (каждую неделю в воскресенье в 10:00)
    scheduler.scheduler.add_job(
        gpt_scheduler.schedule_mood_trend_analysis,
        'cron',
        day_of_week='sun',
        hour=10,
        minute=0,
        id='gpt_mood_analysis',
        name='Анализ трендов настроений'
    )
    
    # Генерация вопросов (каждые 3 дня в 12:00)
    scheduler.scheduler.add_job(
        gpt_scheduler.schedule_question_generation,
        'cron',
        hour=12,
        minute=0,
        id='gpt_question_generation',
        name='Генерация новых вопросов'
    )
    
    # Очистка старых задач (каждую неделю в воскресенье в 2:00)
    scheduler.scheduler.add_job(
        gpt_scheduler.cleanup_old_tasks,
        'cron',
        day_of_week='sun',
        hour=2,
        minute=0,
        id='gpt_cleanup',
        name='Очистка старых GPT задач'
    )
    
    logger.info("✅ GPT задачи зарегистрированы в планировщике")
