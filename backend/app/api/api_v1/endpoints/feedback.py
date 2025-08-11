from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import User, Feedback, FeedbackType, FeedbackStatus
from app.schemas.feedback import Feedback as FeedbackSchema, FeedbackCreate, FeedbackUpdate, FeedbackList
from app.services.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=FeedbackSchema)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправить обратную связь"""
    feedback = Feedback(
        user_id=current_user.id,
        feedback_type=feedback_data.feedback_type,
        subject=feedback_data.subject,
        message=feedback_data.message
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.get("/", response_model=List[FeedbackSchema])
def get_user_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить обратную связь пользователя"""
    feedback = db.query(Feedback).join(User, Feedback.user_id == User.id).filter(
        Feedback.user_id == current_user.id
    ).order_by(Feedback.created_at.desc()).all()
    
    return feedback


@router.get("/{feedback_id}", response_model=FeedbackSchema)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить конкретное обращение"""
    feedback = db.query(Feedback).join(User, Feedback.user_id == User.id).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обращение не найдено"
        )
    
    return feedback
