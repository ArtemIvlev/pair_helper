from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EventKindEnum(str, enum.Enum):
    SHARED = "shared"
    PRIVATE_FEMALE = "private_female"
    PRIVATE_MALE = "private_male"


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for shared events
    date = Column(DateTime(timezone=True), nullable=False)
    time = Column(DateTime(timezone=True), nullable=True)
    kind = Column(Enum(EventKindEnum), default=EventKindEnum.SHARED)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reminder_minutes = Column(Integer, nullable=True)  # minutes before event
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pair = relationship("Pair", back_populates="calendar_events")
    user = relationship("User", back_populates="calendar_events")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title='{self.title}', pair_id={self.pair_id})>"
