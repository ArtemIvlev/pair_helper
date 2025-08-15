import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from collections import deque
import threading

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.analytics import UsageEvent

logger = logging.getLogger(__name__)

# In-memory очередь для событий (fallback механизм)
_event_queue = deque(maxlen=1000)  # Ограничиваем размер очереди
_queue_lock = threading.Lock()


def _now_utc() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


def _save_event_sync(event: UsageEvent) -> bool:
	"""Синхронная функция для сохранения события в БД"""
	session = None
	try:
		session = SessionLocal()
		session.add(event)
		session.commit()
		logger.debug(f"Analytics: saved event {event.method} {event.route} {event.status}")
		return True
	except SQLAlchemyError as e:
		logger.error(f"Analytics: SQL error saving event: {e}")
		if session:
			session.rollback()
		return False
	except Exception as e:
		logger.error(f"Analytics: unexpected error saving event: {e}")
		if session:
			session.rollback()
		return False
	finally:
		if session:
			try:
				session.close()
			except Exception:
				pass


def _save_event_with_retry(event: UsageEvent, max_retries: int = 2) -> bool:
	"""Сохранение события с повторными попытками"""
	for attempt in range(max_retries + 1):
		if _save_event_sync(event):
			return True
		
		if attempt < max_retries:
			logger.warning(f"Analytics: retry {attempt + 1}/{max_retries + 1}")
			time.sleep(0.1 * (attempt + 1))
	
	# Если все попытки неудачны, добавляем в очередь
	with _queue_lock:
		_event_queue.append({
			'method': event.method,
			'route': event.route,
			'status': event.status,
			'duration_ms': event.duration_ms,
			'telegram_id': event.telegram_id,
			'ts': event.ts.isoformat()
		})
	
	logger.warning(f"Analytics: event queued after {max_retries + 1} failed attempts")
	return False


async def _process_event_queue():
	"""Асинхронная обработка очереди событий"""
	while True:
		try:
			# Обрабатываем события из очереди
			with _queue_lock:
				if not _event_queue:
					break
				
				queued_event = _event_queue.popleft()
			
			# Создаем объект события
			event = UsageEvent(
				ts=datetime.fromisoformat(queued_event['ts']),
				method=queued_event['method'],
				route=queued_event['route'],
				status=queued_event['status'],
				duration_ms=queued_event['duration_ms'],
				telegram_id=queued_event['telegram_id']
			)
			
			# Пытаемся сохранить
			loop = asyncio.get_running_loop()
			success = await loop.run_in_executor(None, _save_event_sync, event)
			
			if not success:
				# Возвращаем обратно в очередь
				with _queue_lock:
					_event_queue.appendleft(queued_event)
					break  # Прерываем обработку, чтобы не зациклиться
			
		except Exception as e:
			logger.error(f"Analytics: error processing queued event: {e}")
			break


class UsageAnalyticsMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		if not settings.ANALYTICS_ENABLED:
			return await call_next(request)

		start = time.perf_counter()
		method = request.method
		route = request.url.path

		# Получаем telegram_id до выполнения запроса
		telegram_id: Optional[int] = getattr(getattr(request, "state", None), "telegram_id", None)

		# Выполняем запрос и обрабатываем возможные исключения
		try:
			response = await call_next(request)
			status = response.status_code
		except Exception as e:
			# Если произошла необработанная ошибка, считаем её 500
			logger.error(f"UsageAnalyticsMiddleware: unhandled exception: {e}")
			status = 500
			# Создаем фиктивный response для совместимости
			from starlette.responses import Response
			response = Response(status_code=status)

		duration_ms = int((time.perf_counter() - start) * 1000)

		# Создаем событие
		event = UsageEvent(
			ts=_now_utc(),
			method=method,
			route=route,
			status=status,
			duration_ms=duration_ms,
			telegram_id=telegram_id,
		)

		# Сохраняем событие в фоне
		try:
			loop = asyncio.get_running_loop()
			loop.run_in_executor(None, _save_event_with_retry, event)
		except Exception as e:
			logger.error(f"UsageAnalyticsMiddleware: failed to schedule event save: {e}")
			# Fallback в лог
			logger.warning(f"Analytics fallback log: {method} {route} {status} {duration_ms}ms")

		# Пытаемся обработать очередь событий
		try:
			asyncio.create_task(_process_event_queue())
		except Exception as e:
			logger.error(f"UsageAnalyticsMiddleware: failed to process event queue: {e}")

		return response


# Функция для получения статистики очереди (для мониторинга)
def get_queue_stats() -> Dict[str, Any]:
	with _queue_lock:
		return {
			'queue_size': len(_event_queue),
			'max_size': _event_queue.maxlen
		}

