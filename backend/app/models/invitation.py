from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import secrets

from app.core.database import Base

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_telegram_id = Column(BigInteger, nullable=True)  # Заполняется когда приглашенный регистрируется
    code = Column(String(32), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Отношения
    inviter = relationship("User", back_populates="sent_invitations")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.code:
            self.code = secrets.token_urlsafe(16)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=7)  # Срок действия 7 дней
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
