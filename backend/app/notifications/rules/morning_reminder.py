from __future__ import annotations

from datetime import timedelta, date, datetime, timezone
from typing import Dict, Any, Iterable

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User, Pair, Mood, UserAnswer, UsageEvent
from ..base import ScheduledTrigger, Rule, register_rule, msk_to_utc_cron


class MorningReminderRule:
    id = "morning_reminder"
    trigger = ScheduledTrigger(cron=msk_to_utc_cron(10, 0))  # Каждый день в 10:00 MSK
    priority = 90

    def select_targets(self, ctx: Dict[str, Any]) -> Iterable[User]:
        session = SessionLocal()
        try:
            # Получаем всех пользователей, у которых есть пара
            # Используем UNION для объединения user1 и user2 из пар
            from sqlalchemy import or_
            
            # Получаем всех пользователей, которые являются user1 или user2 в активных парах
            users_with_pairs = session.query(User).join(
                Pair, 
                or_(User.id == Pair.user1_id, User.id == Pair.user2_id)
            ).filter(Pair.status == "active").all()
            
            return users_with_pairs
        finally:
            session.close()

    def is_allowed(self, ctx: Dict[str, Any], user: User) -> bool:
        # Проверяем, заходил ли пользователь в приложение за последние 4 часа
        session = SessionLocal()
        try:
            four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=4)
            
            # Проверяем активность через UsageEvent за последние 4 часа
            recent_activity = session.query(UsageEvent).filter(
                UsageEvent.telegram_id == user.telegram_id,
                UsageEvent.ts >= four_hours_ago
            ).first()
            
            # Если пользователь был активен за последние 4 часа, не отправляем напоминание
            return not recent_activity
            
        finally:
            session.close()

    def cooldown(self):
        return timedelta(hours=24)

    def make_dedupe(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        return {"entity_type": None, "entity_id": None, "date_bucket": date.today().isoformat()}

    def render(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        webapp_base_url = settings.TELEGRAM_WEBAPP_URL or "https://gallery.homoludens.photos/pulse_of_pair/"
        webapp_url = f"{webapp_base_url}?tgWebAppStartParam=main"
        
        import random
        greetings = [
            "Доброе утро! Загляните в приложение — вдруг там найдётся тема, которая сделает день теплее.",
            "Доброе утро! В приложении уже ждёт что-то, что может сделать этот день особенным.",
            "Доброе утро! Пара минут в приложении — и у вас появится повод улыбнуться друг другу.",
            "Доброе утро! В приложении есть вопрос, который может стать началом интересного разговора.",
            "Доброе утро! Сегодня в приложении вас ждёт что-то для вашей пары.",
            "Доброе утро! Загляните — возможно, там найдётся идея для тёплого момента сегодня.",
            "Доброе утро! Несколько минут в приложении — и день начнётся с маленького, но важного жеста.",
            "Доброе утро! Сегодня в приложении есть повод для новой улыбки.",
            "Доброе утро! Может быть, сегодняшний вопрос в приложении станет вашим маленьким открытием.",
            "Доброе утро! В приложении вас ждёт тема, о которой стоит поговорить сегодня.",
            "Доброе утро! Загляните — там есть что-то, что может скрасить утро.",
            "Доброе утро! Пара минут в приложении — и день получит немного тепла.",
            "Доброе утро! Сегодня в приложении вас ждёт вопрос, который может удивить.",
            "Доброе утро! Откройте приложение — вдруг там есть идея для приятного вечера.",
            "Доброе утро! Сегодняшний день можно начать с небольшой совместной активности.",
            "Доброе утро! В приложении уже готов вопрос для вас двоих.",
            "Доброе утро! Возможно, в приложении вы найдёте тему для вдохновляющего разговора.",
            "Доброе утро! Сегодня в приложении есть то, что может добавить тепла вашему дню.",
            "Доброе утро! Загляните — там вас ждёт маленький повод для улыбки.",
            "Доброе утро! Пара минут в приложении — и у вас появится новая общая тема.",
            "Доброе утро! Сегодняшний вопрос в приложении может стать началом чего-то важного.",
            "Доброе утро! Загляните — возможно, там есть идея, которую вы захотите обсудить.",
            "Доброе утро! Несколько минут вместе в приложении — и день начнётся иначе.",
            "Доброе утро! В приложении вас ждёт маленькая деталь, которая может изменить настроение.",
            "Доброе утро! Сегодня там есть что-то, что стоит обсудить именно вам двоим.",
            "Доброе утро! Возможно, сегодня в приложении вы найдёте что-то, что вас сблизит.",
            "Доброе утро! В приложении уже ждёт вопрос для вашего утреннего разговора.",
            "Доброе утро! Несколько минут в приложении могут подарить новый взгляд на привычные вещи.",
            "Доброе утро! Сегодня там есть тема, которая может добавить света в этот день.",
            "Доброе утро! Загляните — вдруг именно сегодня вас ждёт что-то особенное."
        ]
        text = "🌅 " + random.choice(greetings)
        
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "Отметить настроение", "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=mood"}},
                    {"text": "Ответить на вопрос", "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=questions"}}
                ],
                [
                    {"text": "Открыть приложение", "web_app": {"url": webapp_url}}
                ]
            ]
        }
        
        return {"text": text, "reply_markup": reply_markup}


# Регистрация правила при импорте модуля
register_rule(MorningReminderRule())


