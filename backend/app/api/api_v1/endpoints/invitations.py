from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationResponse, InvitationLink

router = APIRouter()

@router.get("/test")
def test_invitations():
    """Тестовый эндпоинт для проверки работы роутера"""
    return {"message": "Invitations router is working!"}

@router.post("/generate", response_model=InvitationResponse)
def generate_invitation(inviter_telegram_id: int, db: Session = Depends(get_db)):
    """Генерирует приглашение для пользователя"""
    # Находим пользователя по Telegram ID
    user = db.query(User).filter(User.telegram_id == inviter_telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Создаем приглашение
    invitation = Invitation(inviter_id=user.id)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return invitation

@router.get("/{code}", response_model=InvitationLink)
def get_invitation_info(code: str, db: Session = Depends(get_db)):
    """Получает информацию о приглашении по коду"""
    invitation = db.query(Invitation).filter(Invitation.code == code).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")
    
    if not invitation.is_valid:
        raise HTTPException(status_code=400, detail="Приглашение недействительно")
    
    return InvitationLink(
        code=invitation.code,
        inviter_name=invitation.inviter.first_name,
        expires_at=invitation.expires_at,
        is_valid=invitation.is_valid
    )

@router.post("/{code}/use")
def use_invitation(code: str, invitee_telegram_id: int, db: Session = Depends(get_db)):
    """Использует приглашение и создает пару"""
    
    invitation = db.query(Invitation).filter(Invitation.code == code).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")
    
    if not invitation.is_valid:
        raise HTTPException(status_code=400, detail="Приглашение недействительно")
    
    # Проверяем, что приглашенный пользователь существует
    invitee = db.query(User).filter(User.telegram_id == invitee_telegram_id).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="Приглашенный пользователь не найден")
    
    # Проверяем, что пользователи не в паре уже
    from app.models.pair import Pair
    existing_pair = db.query(Pair).filter(
        ((Pair.user1_id == invitation.inviter_id) & (Pair.user2_id == invitee.id)) |
        ((Pair.user1_id == invitee.id) & (Pair.user2_id == invitation.inviter_id))
    ).first()
    
    if existing_pair:
        raise HTTPException(status_code=400, detail="Пользователи уже в паре")
    
    # Создаем пару
    pair = Pair(user1_id=invitation.inviter_id, user2_id=invitee.id)
    db.add(pair)
    
    # Отмечаем приглашение как использованное
    invitation.is_used = True
    invitation.invitee_telegram_id = invitee_telegram_id
    
    db.commit()
    
    return {"message": "Пара создана успешно"}

@router.get("/user/{telegram_id}", response_model=List[InvitationResponse])
def get_user_invitations(telegram_id: int, db: Session = Depends(get_db)):
    """Получает все приглашения пользователя"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    invitations = db.query(Invitation).filter(Invitation.inviter_id == user.id).all()
    return invitations
