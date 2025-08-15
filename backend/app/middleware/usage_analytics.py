import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.analytics import UsageEvent

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


def _save_event_sync(event: UsageEvent) -> None:
	"""Синхронная функция для сохранения события в БД с обработкой ошибок"""
	session = None
	try:
		session = SessionLocal()
		session.add(event)
		session.commit()
		logger.debug(f"Analytics: saved event {event.method} {event.route} {event.status}")
	except SQLAlchemyError as e:
		logger.error(f"Analytics: SQL error saving event: {e}")
		if session:
			session.rollback()
	except Exception as e:
		logger.error(f"Analytics: unexpected error saving event: {e}")
		logger.debug(f"Analytics: event details - {event.method} {event.route} {event.status}")
		if session:
			session.rollback()
	finally:
		if session:
			try:
				session.close()
			except Exception:
				pass


def _save_event_with_retry(event: UsageEvent, max_retries: int = 2) -> None:
	"""Сохранение события с повторными попытками"""
	for attempt in range(max_retries + 1):
		try:
			_save_event_sync(event)
			return  # Успешно сохранено
		except Exception as e:
			if attempt == max_retries:
				logger.error(f"Analytics: failed to save event after {max_retries + 1} attempts: {e}")
				# Последняя попытка - записываем в лог как fallback
				logger.warning(f"Analytics fallback log: {event.method} {event.route} {event.status} {event.duration_ms}ms")
			else:
				logger.warning(f"Analytics: retry {attempt + 1}/{max_retries + 1} for event: {e}")
				time.sleep(0.1 * (attempt + 1))  # Экспоненциальная задержка


class UsageAnalyticsMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		if not settings.ANALYTICS_ENABLED:
			return await call_next(request)

		# Пропускаем внутренние API - они не нужны для аналитики пользователей
		if request.url.path.startswith("/api/v1/internal"):
			return await call_next(request)

		start = time.perf_counter()
		method = request.method
		route = request.url.path

		# Получаем telegram_id до выполнения запроса
		telegram_id: Optional[int] = getattr(getattr(request, "state", None), "telegram_id", None)

		try:
			logger.debug(f"UsageAnalyticsMiddleware: processing {method} {route}")
		except Exception:
			pass

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

		# Сохраняем событие в фоне с повторными попытками
		try:
			# Используем run_in_executor для асинхронности
			loop = asyncio.get_running_loop()
			loop.run_in_executor(None, _save_event_with_retry, event)
		except Exception as e:
			# Если не удалось запустить в executor, записываем в лог
			logger.error(f"UsageAnalyticsMiddleware: failed to schedule event save: {e}")
			logger.warning(f"Analytics fallback log: {method} {route} {status} {duration_ms}ms")

		return response

