from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvitationBase(BaseModel):
    pass

class InvitationCreate(InvitationBase):
    inviter_id: int

class InvitationResponse(InvitationBase):
    id: int
    inviter_id: int
    invitee_telegram_id: Optional[int] = None
    code: str
    is_used: bool
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True

class InvitationLink(BaseModel):
    code: str
    inviter_name: str
    expires_at: datetime
    is_valid: bool
