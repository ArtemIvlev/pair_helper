from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PeriodicityEnum(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Ritual(Base):
    __tablename__ = "rituals"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    periodicity = Column(Enum(PeriodicityEnum), default=PeriodicityEnum.DAILY)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pair = relationship("Pair", back_populates="rituals")
    checks = relationship("RitualCheck", back_populates="ritual")

    def __repr__(self):
        return f"<Ritual(id={self.id}, title='{self.title}', pair_id={self.pair_id})>"


class RitualCheck(Base):
    __tablename__ = "ritual_checks"

    id = Column(Integer, primary_key=True, index=True)
    ritual_id = Column(Integer, ForeignKey("rituals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ritual = relationship("Ritual", back_populates="checks")
    user = relationship("User", back_populates="ritual_checks")

    def __repr__(self):
        return f"<RitualCheck(id={self.id}, ritual_id={self.ritual_id}, user_id={self.user_id}, done={self.done})>"
