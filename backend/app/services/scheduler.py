import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)


class NotificationScheduler:
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.notification_engine: Optional[NotificationEngine] = None
        
    def start(self, notification_engine: NotificationEngine):
        """Запускает планировщик уведомлений"""
        self.notification_engine = notification_engine
        
        # Создаем планировщик с асинхронным исполнителем
        executors = {
            'default': AsyncIOExecutor()
        }
        jobstores = {
            'default': MemoryJobStore()
        }
        
        self.scheduler = AsyncIOScheduler(
            executors=executors,
            jobstores=jobstores,
            timezone='UTC'
        )
        
        # Добавляем задачу для запуска уведомлений каждый час
        # Это позволит запускать правила, которые должны выполняться в определенное время
        self.scheduler.add_job(
            self._run_scheduled_notifications,
            CronTrigger(minute=0),  # Каждый час в :00
            id='scheduled_notifications',
            name='Запуск уведомлений по расписанию',
            replace_existing=True
        )
        
        # Регистрируем GPT задачи
        self._register_gpt_jobs()
        
        # Запускаем планировщик
        self.scheduler.start()
        logger.info("🚀 Планировщик уведомлений запущен")
        
    def stop(self):
        """Останавливает планировщик"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("🛑 Планировщик уведомлений остановлен")
    
    def _register_gpt_jobs(self):
        """Регистрирует GPT задачи в планировщике"""
        try:
            from app.gpt.scheduler.gpt_scheduler import register_gpt_jobs
            register_gpt_jobs()
            logger.info("✅ GPT задачи зарегистрированы в планировщике")
        except ImportError:
            logger.warning("⚠️ GPT модуль не найден, пропускаем регистрацию GPT задач")
        except Exception as e:
            logger.error(f"❌ Ошибка регистрации GPT задач: {e}")
            
    async def _run_scheduled_notifications(self):
        """Запускает проверку и отправку уведомлений по расписанию"""
        try:
            if self.notification_engine:
                await self.notification_engine.run_scheduled()
                logger.info("✅ Уведомления по расписанию обработаны")
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске уведомлений по расписанию: {e}")


# Глобальный экземпляр планировщика
scheduler = NotificationScheduler()


