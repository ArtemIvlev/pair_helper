import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.analytics import UsageEvent

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
	return datetime.now(timezone.utc).replace(tzinfo=None)


def _save_event_sync(event: UsageEvent) -> None:
	try:
		session: Session = SessionLocal()
		session.add(event)
		session.commit()
		# Эксплицитное закрытие
		session.close()
	except Exception as e:
		try:
			logger.debug(f"Analytics: failed to save event: {e}")
		except Exception:
			pass
		return


class UsageAnalyticsMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		if not settings.ANALYTICS_ENABLED:
			return await call_next(request)

		start = time.perf_counter()
		method = request.method
		route = request.url.path

		try:
			logger.debug(f"UsageAnalyticsMiddleware: processing {method} {route}")
		except Exception:
			pass

		response = await call_next(request)

		duration_ms = int((time.perf_counter() - start) * 1000)
		status = response.status_code

		telegram_id: Optional[int] = getattr(getattr(request, "state", None), "telegram_id", None)

		event = UsageEvent(
			ts=_now_utc(),
			method=method,
			route=route,
			status=status,
			duration_ms=duration_ms,
			telegram_id=telegram_id,
		)

		# Fire-and-forget в отдельном фоне, чтобы не блокировать ответ
		asyncio.get_running_loop().run_in_executor(None, _save_event_sync, event)

		return response

