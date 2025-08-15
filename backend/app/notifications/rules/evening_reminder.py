from __future__ import annotations

from datetime import timedelta, date, datetime, timezone
from typing import Dict, Any, Iterable, Optional, Tuple

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import User, Pair, Mood, UserAnswer, UsageEvent, Question, PairDailyQuestion
from app.models.tune import PairDailyTuneQuestion, TuneAnswer, TuneQuizQuestion
from ..base import ScheduledTrigger, Rule, register_rule, msk_to_utc_cron


class EveningReminderRule:
    id = "evening_reminder"
    trigger = ScheduledTrigger(cron=msk_to_utc_cron(20, 0))  # Каждый день в 20:00 MSK
    priority = 85

    def select_targets(self, ctx: Dict[str, Any]) -> Iterable[User]:
        session = SessionLocal()
        try:
            # Получаем всех пользователей, у которых есть активная пара
            from sqlalchemy import or_
            
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

    def _get_partner_info(self, session, user: User) -> Tuple[Optional[User], Optional[Pair]]:
        """Получить информацию о партнере и паре"""
        pair = session.query(Pair).filter(
            (Pair.user1_id == user.id) | (Pair.user2_id == user.id),
            Pair.status == "active"
        ).first()
        
        if not pair:
            return None, None
            
        partner_id = pair.user2_id if pair.user1_id == user.id else pair.user1_id
        partner = session.query(User).filter(User.id == partner_id).first()
        
        return partner, pair

    def _check_daily_question_status(self, session, user: User, partner: User, pair: Pair) -> Tuple[bool, bool, Optional[Question]]:
        """Проверить статус вопроса дня"""
        today = date.today()
        
        # Получаем вопрос дня для пары
        daily_question = session.query(PairDailyQuestion).filter(
            PairDailyQuestion.pair_id == pair.id,
            PairDailyQuestion.date == today
        ).first()
        
        if not daily_question:
            return False, False, None
            
        question = session.query(Question).filter(Question.id == daily_question.question_id).first()
        if not question:
            return False, False, None
            
        # Проверяем ответы
        user_answered = session.query(UserAnswer).filter(
            UserAnswer.user_id == user.id,
            UserAnswer.question_id == question.id
        ).first() is not None
        
        partner_answered = session.query(UserAnswer).filter(
            UserAnswer.user_id == partner.id,
            UserAnswer.question_id == question.id
        ).first() is not None
        
        return user_answered, partner_answered, question

    def _check_tune_status(self, session, user: User, partner: User, pair: Pair) -> Tuple[bool, bool, Optional[TuneQuizQuestion]]:
        """Проверить статус сонастройки"""
        today = date.today()
        
        # Получаем вопрос сонастройки для пары
        tune_question = session.query(PairDailyTuneQuestion).filter(
            PairDailyTuneQuestion.pair_id == pair.id,
            PairDailyTuneQuestion.date == today
        ).first()
        
        if not tune_question:
            return False, False, None
            
        question = session.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == tune_question.question_id).first()
        if not question:
            return False, False, None
            
        # Проверяем ответы каждого пользователя
        # Каждый должен ответить 2 раза: о себе и о партнере
        
        # Мои ответы
        my_about_me = session.query(TuneAnswer).filter(
            TuneAnswer.pair_id == pair.id,
            TuneAnswer.question_id == question.id,
            TuneAnswer.author_user_id == user.id,
            TuneAnswer.subject_user_id == user.id
        ).first()
        
        my_about_partner = session.query(TuneAnswer).filter(
            TuneAnswer.pair_id == pair.id,
            TuneAnswer.question_id == question.id,
            TuneAnswer.author_user_id == user.id,
            TuneAnswer.subject_user_id == partner.id
        ).first()
        
        # Ответы партнера
        partner_about_himself = session.query(TuneAnswer).filter(
            TuneAnswer.pair_id == pair.id,
            TuneAnswer.question_id == question.id,
            TuneAnswer.author_user_id == partner.id,
            TuneAnswer.subject_user_id == partner.id
        ).first()
        
        partner_about_me = session.query(TuneAnswer).filter(
            TuneAnswer.pair_id == pair.id,
            TuneAnswer.question_id == question.id,
            TuneAnswer.author_user_id == partner.id,
            TuneAnswer.subject_user_id == user.id
        ).first()
        
        # Пользователь завершил сонастройку если ответил о себе И о партнере
        user_completed = my_about_me is not None and my_about_partner is not None
        partner_completed = partner_about_himself is not None and partner_about_me is not None
        
        return user_completed, partner_completed, question

    def _check_partner_activity(self, session, partner: User) -> bool:
        """Проверить активность партнера за последние 4 часа"""
        four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=4)
        
        # Проверяем активность через UsageEvent
        recent_activity = session.query(UsageEvent).filter(
            UsageEvent.telegram_id == partner.telegram_id,
            UsageEvent.ts >= four_hours_ago
        ).first()
        
        return recent_activity is not None

    def render(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        session = SessionLocal()
        try:
            partner, pair = self._get_partner_info(session, user)
            if not partner or not pair:
                return None  # Нет пары - не отправляем
            
            webapp_base_url = settings.TELEGRAM_WEBAPP_URL or "https://gallery.homoludens.photos/pulse_of_pair/"
            
            # Проверяем статус вопроса дня
            user_answered_daily, partner_answered_daily, daily_question = self._check_daily_question_status(
                session, user, partner, pair
            )
            
            # Проверяем статус сонастройки
            user_answered_tune, partner_answered_tune, tune_question = self._check_tune_status(
                session, user, partner, pair
            )
            
            # Проверяем активность партнера
            partner_active = self._check_partner_activity(session, partner)
            
            # Формируем текст в зависимости от ситуации
            text_parts = []
            buttons = []
            
            # Если оба ответили на все - не отправляем
            if (user_answered_daily and partner_answered_daily and 
                user_answered_tune and partner_answered_tune):
                return None
            
            # Анализ вопроса дня
            if daily_question:
                if not user_answered_daily and partner_answered_daily:
                    text_parts.append(f"💬 {partner.first_name} ответил(а) на вопрос дня, а вы ещё нет!")
                    buttons.append({
                        "text": "Ответить на вопрос дня", 
                        "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=questions"}
                    })
                elif not user_answered_daily and not partner_answered_daily:
                    text_parts.append("💬 Вопрос дня ждёт ваших ответов!")
                    buttons.append({
                        "text": "Ответить на вопрос дня", 
                        "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=questions"}
                    })
            
            # Анализ сонастройки
            if tune_question:
                if not user_answered_tune and partner_answered_tune:
                    text_parts.append(f"🎯 {partner.first_name} прошёл(а) сонастройку, а вы ещё нет!")
                    buttons.append({
                        "text": "Пройти сонастройку", 
                        "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=tune"}
                    })
                elif not user_answered_tune and not partner_answered_tune:
                    text_parts.append("🎯 Сонастройка ждёт вас обоих!")
                    buttons.append({
                        "text": "Пройти сонастройку", 
                        "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=tune"}
                    })
            
            # Если партнер не активен и нет конкретных задач
            if not partner_active and not text_parts:
                text_parts.append(f"🌙 {partner.first_name} тоже не проявлял(а) активности. Может, стоит вместе заглянуть в приложение?")
                buttons.extend([
                    {"text": "Отметить настроение", "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=mood"}},
                    {"text": "Открыть приложение", "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=main"}}
                ])
            
            # Если есть конкретные задачи, добавляем общую кнопку
            if text_parts and len(buttons) < 2:
                buttons.append({
                    "text": "Открыть приложение", 
                    "web_app": {"url": f"{webapp_base_url}?tgWebAppStartParam=main"}
                })
            
            text = " ".join(text_parts)
            
            reply_markup = {
                "inline_keyboard": [buttons] if len(buttons) == 1 else [buttons[:2], buttons[2:]] if len(buttons) > 2 else [buttons]
            }
            
            return {"text": text, "reply_markup": reply_markup}
            
        finally:
            session.close()


# Регистрация правила при импорте модуля
register_rule(EveningReminderRule())
