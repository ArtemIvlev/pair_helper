from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    settings_json = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

    # Relationships
    pairs_as_user1 = relationship("Pair", foreign_keys="Pair.user1_id", back_populates="user1")
    pairs_as_user2 = relationship("Pair", foreign_keys="Pair.user2_id", back_populates="user2")
    pair_invites = relationship("PairInvite", back_populates="owner")

    moods = relationship("Mood", back_populates="user")
    appreciations = relationship("Appreciation", back_populates="user")
    ritual_checks = relationship("RitualCheck", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    female_cycle = relationship("FemaleCycle", back_populates="user", uselist=False)
    female_cycle_logs = relationship("FemaleCycleLog", back_populates="user")
    emotion_notes = relationship("EmotionNote", back_populates="user")
    sent_invitations = relationship("Invitation", back_populates="inviter")
    question_answers = relationship("UserAnswer", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, first_name='{self.first_name}')>"
