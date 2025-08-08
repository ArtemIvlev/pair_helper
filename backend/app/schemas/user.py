from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    settings_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    telegram_id: int
    created_at: datetime
    settings_json: Dict[str, Any]
    is_active: bool

    class Config:
        from_attributes = True
