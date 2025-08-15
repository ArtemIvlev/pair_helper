from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Announcement(Base):
    """Модель обращений от администрации"""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # HTML контент
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(String(20), default='normal', nullable=False)  # low, normal, high, urgent
    target_audience = Column(String(50), default='all', nullable=False)  # all, active_users, new_users, etc.
    display_settings = Column(JSON, default={})  # Дополнительные настройки отображения
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Announcement(id={self.id}, title='{self.title}', is_active={self.is_active})>"


