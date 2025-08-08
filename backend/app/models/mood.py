from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Mood(Base):
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    mood_code = Column(String, nullable=False)  # joyful, calm, tired, anxious, sad, irritable, grateful
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="moods")

    def __repr__(self):
        return f"<Mood(id={self.id}, user_id={self.user_id}, mood_code='{self.mood_code}')>"


class Appreciation(Base):
    __tablename__ = "appreciations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="appreciations")

    def __repr__(self):
        return f"<Appreciation(id={self.id}, user_id={self.user_id}, text='{self.text[:50]}...')>"
