from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Mood, Appreciation, Pair
from app.schemas.mood import Mood as MoodSchema, MoodCreate, Appreciation as AppreciationSchema, AppreciationCreate
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=MoodSchema)
def create_mood(
    mood_data: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сохранить настроение дня"""
    # Проверяем, что настроение за сегодня ещё не было записано
    today = date.today()
    existing_mood = db.query(Mood).filter(
        Mood.user_id == current_user.id,
        db.func.date(Mood.date) == today
    ).first()
    
    if existing_mood:
        # Обновляем существующее настроение
        existing_mood.mood_code = mood_data.mood_code
        existing_mood.note = mood_data.note
        db.commit()
        db.refresh(existing_mood)
        return existing_mood
    
    # Создаём новое настроение
    mood = Mood(
        user_id=current_user.id,
        date=datetime.utcnow(),
        mood_code=mood_data.mood_code,
        note=mood_data.note
    )
    
    db.add(mood)
    db.commit()
    db.refresh(mood)
    
    return mood


@router.get("/", response_model=List[MoodSchema])
def get_moods(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить настроения пользователя и партнёра"""
    # Получаем пару пользователя
    pair = db.query(Pair).filter(
        (Pair.user1_id == current_user.id) | (Pair.user2_id == current_user.id),
        Pair.status == "active"
    ).first()
    
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная пара не найдена"
        )
    
    # Определяем ID партнёра
    partner_id = pair.user2_id if pair.user1_id == current_user.id else pair.user1_id
    
    # Строим запрос
    query = db.query(Mood).filter(
        Mood.user_id.in_([current_user.id, partner_id])
    )
    
    if from_date:
        query = query.filter(db.func.date(Mood.date) >= from_date)
    
    if to_date:
        query = query.filter(db.func.date(Mood.date) <= to_date)
    
    moods = query.order_by(Mood.date.desc()).all()
    
    return moods


@router.post("/appreciation", response_model=AppreciationSchema)
def create_appreciation(
    appreciation_data: AppreciationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сохранить признание/благодарность дня"""
    # Проверяем, что признание за сегодня ещё не было записано
    today = date.today()
    existing_appreciation = db.query(Appreciation).filter(
        Appreciation.user_id == current_user.id,
        db.func.date(Appreciation.date) == today
    ).first()
    
    if existing_appreciation:
        # Обновляем существующее признание
        existing_appreciation.text = appreciation_data.text
        db.commit()
        db.refresh(existing_appreciation)
        return existing_appreciation
    
    # Создаём новое признание
    appreciation = Appreciation(
        user_id=current_user.id,
        date=datetime.utcnow(),
        text=appreciation_data.text
    )
    
    db.add(appreciation)
    db.commit()
    db.refresh(appreciation)
    
    return appreciation


@router.get("/appreciation", response_model=List[AppreciationSchema])
def get_appreciations(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить признания пользователя и партнёра"""
    # Получаем пару пользователя
    pair = db.query(Pair).filter(
        (Pair.user1_id == current_user.id) | (Pair.user2_id == current_user.id),
        Pair.status == "active"
    ).first()
    
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная пара не найдена"
        )
    
    # Определяем ID партнёра
    partner_id = pair.user2_id if pair.user1_id == current_user.id else pair.user1_id
    
    # Строим запрос
    query = db.query(Appreciation).filter(
        Appreciation.user_id.in_([current_user.id, partner_id])
    )
    
    if from_date:
        query = query.filter(db.func.date(Appreciation.date) >= from_date)
    
    if to_date:
        query = query.filter(db.func.date(Appreciation.date) <= to_date)
    
    appreciations = query.order_by(Appreciation.date.desc()).all()
    
    return appreciations
