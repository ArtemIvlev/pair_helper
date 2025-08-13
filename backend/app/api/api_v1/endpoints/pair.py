from datetime import datetime, timedelta
import secrets
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, Pair, PairInvite
from app.schemas.pair import Pair as PairSchema, PairInvite as PairInviteSchema, PairInviteCreate
from app.services.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/invite", response_model=PairInviteSchema, deprecated=True)
def create_invite(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """DEPRECATED. Создать код-приглашение для партнёра.

    Используйте флоу приглашений через эндпоинты `invitations.*` и регистрацию с `invite_code`.
    """
    logger.warning("DEPRECATED endpoint used: POST /api/v1/pair/invite")
    # Проверяем, что у пользователя нет активной пары
    existing_pair = db.query(Pair).filter(
        (Pair.user1_id == current_user.id) | (Pair.user2_id == current_user.id),
        Pair.status == "active"
    ).first()
    
    if existing_pair:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть активная пара"
        )
    
    # Генерируем уникальный код
    code = secrets.token_urlsafe(8).upper()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    invite = PairInvite(
        code=code,
        owner_user_id=current_user.id,
        expires_at=expires_at
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    return invite


@router.post("/join", response_model=PairSchema, deprecated=True)
def join_pair(
    invite_data: PairInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """DEPRECATED. Присоединиться к паре по коду-приглашению.

    Используйте флоу приглашений через эндпоинты `invitations.*` и регистрацию с `invite_code`.
    """
    logger.warning("DEPRECATED endpoint used: POST /api/v1/pair/join")
    # Находим приглашение
    invite = db.query(PairInvite).filter(
        PairInvite.code == invite_data.code,
        PairInvite.status == "pending",
        PairInvite.expires_at > datetime.utcnow()
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недействительный или просроченный код"
        )
    
    if invite.owner_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя присоединиться к своему приглашению"
        )
    
    # Проверяем, что у пользователя нет активной пары
    existing_pair = db.query(Pair).filter(
        (Pair.user1_id == current_user.id) | (Pair.user2_id == current_user.id),
        Pair.status == "active"
    ).first()
    
    if existing_pair:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть активная пара"
        )
    
    # Создаём пару
    pair = Pair(
        user1_id=invite.owner_user_id,
        user2_id=current_user.id
    )
    
    # Помечаем приглашение как принятое
    invite.status = "accepted"
    
    db.add(pair)
    db.commit()
    db.refresh(pair)
    
    return pair


@router.get("/", response_model=PairSchema)
def get_pair(
    telegram_id: int = Header(..., alias="X-Telegram-User-ID"),
    db: Session = Depends(get_db)
):
    """Получить информацию о паре"""
    # Находим пользователя по Telegram ID
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    pair = db.query(Pair).filter(
        (Pair.user1_id == user.id) | (Pair.user2_id == user.id),
        Pair.status == "active"
    ).first()
    
    if pair:
        # Загружаем данные пользователей
        from sqlalchemy.orm import joinedload
        pair = db.query(Pair).options(
            joinedload(Pair.user1),
            joinedload(Pair.user2)
        ).filter(Pair.id == pair.id).first()
    
    if not pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активная пара не найдена"
        )
    
    return pair
