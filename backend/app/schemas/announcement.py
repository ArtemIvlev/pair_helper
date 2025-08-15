from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AnnouncementBase(BaseModel):
    title: str
    content: str
    is_active: bool = True
    priority: str = "normal"
    target_audience: str = "all"
    display_settings: Optional[Dict[str, Any]] = {}


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[str] = None
    target_audience: Optional[str] = None
    display_settings: Optional[Dict[str, Any]] = None


class Announcement(AnnouncementBase):
    id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnnouncementList(BaseModel):
    announcements: list[Announcement]
    total: int
    page: int
    per_page: int
    pages: int


