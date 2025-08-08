from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FemaleCycle(Base):
    __tablename__ = "female_cycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cycle_start_date = Column(DateTime(timezone=True), nullable=False)
    avg_cycle_length = Column(Integer, nullable=False)  # days
    avg_period_length = Column(Integer, nullable=False)  # days
    visibility_for_partner = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="female_cycle")

    def __repr__(self):
        return f"<FemaleCycle(id={self.id}, user_id={self.user_id})>"


class FemaleCycleLog(Base):
    __tablename__ = "female_cycle_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    symptom_code = Column(String, nullable=True)  # cramping, bloating, mood_swings, etc.
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="female_cycle_logs")

    def __repr__(self):
        return f"<FemaleCycleLog(id={self.id}, user_id={self.user_id}, date={self.date})>"
