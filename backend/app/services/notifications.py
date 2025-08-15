from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Notification, User, Pair
from .telegram import TelegramService


@dataclass
class SendResult:
    sent: bool
    reason: Optional[str] = None


class NotificationService:
    def __init__(self, telegram: Optional[TelegramService] = None):
        self.telegram = telegram or TelegramService()

    def _open_session(self) -> Session:
        return SessionLocal()

    def _make_dedupe_key(
        self,
        n_type: str,
        recipient_user_id: int,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        date_bucket: Optional[str] = None,
    ) -> str:
        parts = [n_type, str(recipient_user_id)]
        if entity_type:
            parts.append(entity_type)
        if entity_id is not None:
            parts.append(str(entity_id))
        if date_bucket:
            parts.append(date_bucket)
        return ":".join(parts)

    async def send(
        self,
        *,
        n_type: str,
        recipient: User,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        pair: Optional[Pair] = None,
        actor: Optional[User] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        date_bucket: Optional[str] = None,
        cooldown: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        if not recipient.telegram_id:
            return SendResult(False, "no_telegram_id")

        dedupe_key = self._make_dedupe_key(
            n_type, recipient.id, entity_type, entity_id, date_bucket
        )

        session = self._open_session()
        try:
            # Проверка кулдауна по типу/получателю/сущности
            q = session.query(Notification).filter(
                Notification.type == n_type,
                Notification.recipient_user_id == recipient.id,
            )
            if entity_type:
                q = q.filter(Notification.entity_type == entity_type)
            if entity_id is not None:
                q = q.filter(Notification.entity_id == entity_id)

            if cooldown:
                cutoff = datetime.utcnow() - cooldown
                q = q.filter(Notification.sent_at >= cutoff)

            recently = q.order_by(Notification.sent_at.desc()).first()
            if recently:
                return SendResult(False, "cooldown")

            # Отправка
            await self.telegram.send_message(chat_id=recipient.telegram_id, text=text, reply_markup=reply_markup)

            # Лог
            record = Notification(
                type=n_type,
                recipient_user_id=recipient.id,
                pair_id=pair.id if pair else None,
                actor_user_id=actor.id if actor else None,
                entity_type=entity_type,
                entity_id=entity_id,
                metadata_json=metadata or {},
            )
            session.add(record)
            session.commit()

            return SendResult(True)
        finally:
            session.close()


