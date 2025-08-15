from __future__ import annotations

from datetime import timedelta, date
from typing import Dict, Any, Iterable

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User, Pair
from ..base import ScheduledTrigger, Rule, register_rule


class DailyCheckinRule:
    id = "daily_checkin"
    trigger = ScheduledTrigger(cron="0 9 * * *")  # Каждый день в 9:00
    priority = 100

    def select_targets(self, ctx: Dict[str, Any]) -> Iterable[User]:
        session = SessionLocal()
        try:
            # Получаем только пользователей с парами
            from sqlalchemy import or_
            users_with_pairs = session.query(User).join(
                Pair, 
                or_(User.id == Pair.user1_id, User.id == Pair.user2_id)
            ).filter(Pair.status == "active").all()
            return users_with_pairs
        finally:
            session.close()

    def is_allowed(self, ctx: Dict[str, Any], user: User) -> bool:
        # Здесь можно читать user.settings_json для тихих часов и отключения типа
        return True

    def cooldown(self):
        return timedelta(hours=24)

    def make_dedupe(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        return {"entity_type": None, "entity_id": None, "date_bucket": date.today().isoformat()}

    def render(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        webapp_base_url = settings.TELEGRAM_WEBAPP_URL or "https://gallery.homoludens.photos/pulse_of_pair/"
        webapp_url = f"{webapp_base_url}?tgWebAppStartParam=mood"
        text = "Доброе утро! Как вы сегодня? Отметьте своё настроение."
        reply_markup = {
            "inline_keyboard": [[
                {"text": "Отметить настроение", "web_app": {"url": webapp_url}}
            ]]
        }
        return {"text": text, "reply_markup": reply_markup}


# Регистрация правила при импорте модуля
register_rule(DailyCheckinRule())
