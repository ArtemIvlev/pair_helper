from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRegister, UserUpdate, User as UserSchema

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    
    # Проверяем, не зарегистрирован ли уже пользователь с таким telegram_id
    existing_user = db.query(User).filter(User.telegram_id == user_data.telegram_id).first()
    if existing_user:
        # Если пользователь уже зарегистрирован, но есть код приглашения, используем его
        if user_data.invite_code:
            from app.models.invitation import Invitation
            from app.models.pair import Pair
            
            # Находим приглашение
            invitation = db.query(Invitation).filter(Invitation.code == user_data.invite_code).first()
            if invitation and invitation.is_valid:
                # Проверяем, что пользователи не в паре уже
                existing_pair = db.query(Pair).filter(
                    ((Pair.user1_id == invitation.inviter_id) & (Pair.user2_id == existing_user.id)) |
                    ((Pair.user1_id == existing_user.id) & (Pair.user2_id == invitation.inviter_id))
                ).first()
                
                if not existing_pair:
                    # Создаем пару
                    pair = Pair(user1_id=invitation.inviter_id, user2_id=existing_user.id)
                    db.add(pair)
                    
                    # Отмечаем приглашение как использованное
                    invitation.is_used = True
                    invitation.invitee_telegram_id = user_data.telegram_id
                    
                    db.commit()
        
        return existing_user
    
    # Проверяем соглашения
    if not user_data.accept_terms or not user_data.accept_privacy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо принять все соглашения"
        )
    
    # Создаем нового пользователя
    db_user = User(
        telegram_id=user_data.telegram_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        username=user_data.username,
        settings_json={},
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Если передан код приглашения, создаем пару
    if user_data.invite_code:
        from app.models.invitation import Invitation
        from app.models.pair import Pair
        
        # Находим приглашение
        invitation = db.query(Invitation).filter(Invitation.code == user_data.invite_code).first()
        if invitation and invitation.is_valid:
            # Проверяем, что пользователи не в паре уже
            existing_pair = db.query(Pair).filter(
                ((Pair.user1_id == invitation.inviter_id) & (Pair.user2_id == db_user.id)) |
                ((Pair.user1_id == db_user.id) & (Pair.user2_id == invitation.inviter_id))
            ).first()
            
            if not existing_pair:
                # Создаем пару
                pair = Pair(user1_id=invitation.inviter_id, user2_id=db_user.id)
                db.add(pair)
                
                # Отмечаем приглашение как использованное
                invitation.is_used = True
                invitation.invitee_telegram_id = user_data.telegram_id
                
                db.commit()
    
    return db_user


@router.get("/me", response_model=UserSchema)
def get_current_user(telegram_id: int, db: Session = Depends(get_db)):
    """Получение текущего пользователя по Telegram ID"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получение пользователя по ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Обновление пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Обновляем только переданные поля
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя (мягкое удаление)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "Пользователь успешно удален"}
