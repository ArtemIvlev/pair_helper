from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Произвольный тип уведомления (например, 'daily_checkin', 'inactivity', 'question_reminder', 'tune_reminder', 'mood_update')
    type = Column(String, nullable=False)

    # Получатель уведомления (обязателен)
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Контекст (опционально)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Сущность, к которой относится уведомление (например, question/tune/mood)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)

    # Дополнительные данные для аналитики и отладки
    metadata_json = Column(JSON, default={})

    sent_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships (ленивые, без каскада)
    recipient = relationship("User", foreign_keys=[recipient_user_id])
    actor = relationship("User", foreign_keys=[actor_user_id])
    pair = relationship("Pair")