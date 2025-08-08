from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmotionNote(Base):
    __tablename__ = "emotion_notes"

    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("pairs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    pair = relationship("Pair", back_populates="emotion_notes")
    user = relationship("User", back_populates="emotion_notes")

    def __repr__(self):
        return f"<EmotionNote(id={self.id}, pair_id={self.pair_id}, user_id={self.user_id})>"
