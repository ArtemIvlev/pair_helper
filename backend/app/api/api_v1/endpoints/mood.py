from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from app.core.database import get_db
from app.models import User, Mood, Appreciation, Pair
from app.schemas.mood import Mood as MoodSchema, MoodCreate, Appreciation as AppreciationSchema, AppreciationCreate
from app.services.auth import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=MoodSchema)
async def create_mood(
    mood_data: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сохранить настроение дня"""
    # Проверяем, что настроение за сегодня ещё не было записано
    today = date.today()
    existing_mood = db.query(Mood).filter(
        Mood.user_id == current_user.id,
        func.date(Mood.date) == today
    ).first()
    
    was_update = existing_mood is not None
    
    if existing_mood:
        # Обновляем существующее настроение
        existing_mood.mood_code = mood_data.mood_code
        existing_mood.note = mood_data.note
        db.commit()
        db.refresh(existing_mood)
        mood = existing_mood
    else:
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
    
    # Отправляем уведомление партнеру
    try:
        await send_mood_notification_to_partner(current_user, mood_data.mood_code, was_update, db)
    except Exception as e:
        # Логируем ошибку, но не прерываем сохранение настроения
        print(f"Ошибка отправки уведомления о настроении: {e}")
    
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
    
    # Строим запрос с join для получения информации о пользователях
    query = db.query(Mood).join(User, Mood.user_id == User.id).filter(
        Mood.user_id.in_([current_user.id, partner_id])
    )
    
    if from_date:
        query = query.filter(func.date(Mood.date) >= from_date)
    
    if to_date:
        query = query.filter(func.date(Mood.date) <= to_date)
    
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
        func.date(Appreciation.date) == today
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
        query = query.filter(func.date(Appreciation.date) >= from_date)
    
    if to_date:
        query = query.filter(func.date(Appreciation.date) <= to_date)
    
    appreciations = query.order_by(Appreciation.date.desc()).all()
    
    return appreciations


async def send_mood_notification_to_partner(user: User, mood_code: str, was_update: bool, db: Session):
    """Отправить уведомление партнеру о настроении"""
    # Получаем пару пользователя
    pair = db.query(Pair).filter(
        (Pair.user1_id == user.id) | (Pair.user2_id == user.id),
        Pair.status == "active"
    ).first()
    
    if not pair:
        return  # Нет пары - не отправляем уведомление
    
    # Определяем ID партнёра
    partner_id = pair.user2_id if pair.user1_id == user.id else pair.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()
    
    if not partner:
        return  # Партнер не найден
    
    # Маппинг настроений на эмодзи
    mood_emojis = {
        'joyful': '😊',
        'calm': '😌', 
        'tired': '😴',
        'anxious': '😰',
        'sad': '😢',
        'irritable': '😤',
        'grateful': '🙏'
    }
    
    mood_emoji = mood_emojis.get(mood_code, '😊')
    
    # Формируем текст сообщения
    action = "обновил" if was_update else "отметил"
    text = f"{user.first_name or 'Партнер'} {action} настроение дня: {mood_emoji}"
    
    # Отправляем сообщение через Telegram Bot API
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return
    
    # Создаём диплинк на страницу настроений
    webapp_base_url = settings.TELEGRAM_WEBAPP_URL or "https://gallery.homoludens.photos/pulse_of_pair/"
    webapp_url = f"{webapp_base_url}?tgWebAppStartParam=mood"
    
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    reply_markup = {
        "inline_keyboard": [[
            {"text": "Посмотреть настроение", "web_app": {"url": webapp_url}}
        ]]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(api_url, json={
                "chat_id": partner.telegram_id,
                "text": text,
                "reply_markup": reply_markup
            })
            if resp.status_code != 200:
                # Фолбэк: обычная URL кнопка
                fallback = {
                    "inline_keyboard": [[
                        {"text": "Посмотреть настроение", "url": webapp_url}
                    ]]
                }
                await client.post(api_url, json={
                    "chat_id": partner.telegram_id,
                    "text": text,
                    "reply_markup": fallback
                })
    except Exception as e:
        print(f"Ошибка отправки уведомления о настроении: {e}")
