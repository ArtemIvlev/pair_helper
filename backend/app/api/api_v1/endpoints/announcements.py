from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.announcement import Announcement
from app.schemas.announcement import Announcement as AnnouncementSchema, AnnouncementList
from app.services.auth import get_current_user
from app.models.user import User
from fastapi import Header

router = APIRouter()


@router.get("/", response_model=List[AnnouncementSchema])
@router.get("", response_model=List[AnnouncementSchema])
async def get_announcements(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
    active_only: bool = Query(True, description="Показывать только активные обращения"),
    target_audience: Optional[str] = Query(None, description="Фильтр по целевой аудитории")
):
    """
    Получить список обращений от администрации
    """
    query = db.query(Announcement)
    
    if active_only:
        query = query.filter(Announcement.is_active == True)
    
    # Фильтрация по целевой аудитории
    if target_audience:
        query = query.filter(Announcement.target_audience == target_audience)
    else:
        # Если целевая аудитория не указана, показываем обращения для всех или для активных пользователей
        # Определяем, является ли пользователь активным (например, зарегистрирован более 7 дней назад)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        is_active_user = False
        if current_user and getattr(current_user, 'created_at', None):
            user_created_at = current_user.created_at
            if user_created_at.tzinfo is None:
                user_created_at = user_created_at.replace(tzinfo=timezone.utc)
            is_active_user = user_created_at < week_ago
        
        if is_active_user:
            # Для активных пользователей показываем обращения для всех и для активных пользователей
            query = query.filter(
                (Announcement.target_audience == "all") | 
                (Announcement.target_audience == "active_users")
            )
        else:
            # Для новых пользователей показываем обращения для всех и для новых пользователей
            query = query.filter(
                (Announcement.target_audience == "all") | 
                (Announcement.target_audience == "new_users")
            )
    
    # Сортируем по приоритету и дате создания
    announcements = query.order_by(
        Announcement.priority.desc(),
        Announcement.created_at.desc()
    ).all()
    
    return announcements


@router.get("/{announcement_id}", response_model=AnnouncementSchema)
async def get_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Получить конкретное обращение по ID
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    
    if not announcement.is_active:
        raise HTTPException(status_code=404, detail="Обращение неактивно")
    
    return announcement


@router.get("/active/count")
async def get_active_announcements_count(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Получить количество активных обращений для текущего пользователя
    """
    query = db.query(Announcement).filter(Announcement.is_active == True)
    
    # Определяем, является ли пользователь активным
    from datetime import timedelta
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    is_active_user = False
    if current_user and getattr(current_user, 'created_at', None):
        user_created_at = current_user.created_at
        if user_created_at.tzinfo is None:
            user_created_at = user_created_at.replace(tzinfo=timezone.utc)
        is_active_user = user_created_at < week_ago
    
    if is_active_user:
        query = query.filter(
            (Announcement.target_audience == "all") | 
            (Announcement.target_audience == "active_users")
        )
    else:
        query = query.filter(
            (Announcement.target_audience == "all") | 
            (Announcement.target_audience == "new_users")
        )
    
    count = query.count()
    
    return {"count": count}
