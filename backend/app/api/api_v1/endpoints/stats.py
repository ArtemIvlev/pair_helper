from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analytics import UsageEvent

router = APIRouter()

@router.get("/participation")
def get_participation_stats(
		period_days: int = Query(default=7, ge=1, le=90),
		telegram_id: Optional[int] = Query(default=None),
		db: Session = Depends(get_db),
):
	"""Простая метрика участия по числу запросов в день."""
	since = datetime.utcnow() - timedelta(days=period_days)
	query = (
		db.query(
			func.date_trunc('day', UsageEvent.ts).label('day'),
			func.count().label('requests')
		)
		.filter(UsageEvent.ts >= since)
		.group_by(func.date_trunc('day', UsageEvent.ts))
		.order_by(func.date_trunc('day', UsageEvent.ts))
	)
	if telegram_id is not None:
		query = query.filter(UsageEvent.telegram_id == telegram_id)
	rows = query.all()
	return {"data": [{"day": r.day.isoformat(), "requests": r.requests} for r in rows]}

@router.get("/mood-trend")
def get_mood_trend():
    """Получить тренд настроений"""
    return {"message": "Тренд настроений - в разработке"}
