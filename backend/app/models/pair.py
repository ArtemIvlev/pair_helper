from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class PairStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class Pair(Base):
    __tablename__ = "pairs"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(PairStatus), default=PairStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="pairs_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="pairs_as_user2")
    rituals = relationship("Ritual", back_populates="pair")
    calendar_events = relationship("CalendarEvent", back_populates="pair")
    emotion_notes = relationship("EmotionNote", back_populates="pair")

    def __repr__(self):
        return f"<Pair(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id})>"


class PairInvite(Base):
    __tablename__ = "pair_invites"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(InviteStatus), default=InviteStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="pair_invites")

    def __repr__(self):
        return f"<PairInvite(id={self.id}, code='{self.code}', owner_user_id={self.owner_user_id})>"
