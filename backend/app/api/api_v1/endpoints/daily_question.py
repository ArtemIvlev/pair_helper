from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User, DailyQuestion, Answer, Pair
from app.schemas.daily_question import DailyQuestion as DailyQuestionSchema, Answer as AnswerSchema, AnswerCreate
from app.services.auth import get_current_user

router = APIRouter()


@router.get("/today", response_model=DailyQuestionSchema)
def get_today_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить вопрос дня"""
    # Получаем случайный активный вопрос
    question = db.query(DailyQuestion).filter(
        DailyQuestion.is_active == True
    ).order_by(db.func.random()).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет доступных вопросов"
        )
    
    return question


@router.post("/answer", response_model=AnswerSchema)
def create_answer(
    answer_data: AnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Сохранить ответ на вопрос дня"""
    # Проверяем, что вопрос существует
    question = db.query(DailyQuestion).filter(
        DailyQuestion.id == answer_data.question_id,
        DailyQuestion.is_active == True
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вопрос не найден"
        )
    
    # Проверяем, что ответ за сегодня ещё не был дан
    today = date.today()
    existing_answer = db.query(Answer).filter(
        Answer.user_id == current_user.id,
        Answer.question_id == answer_data.question_id,
        db.func.date(Answer.date) == today
    ).first()
    
    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ответ на этот вопрос уже был дан сегодня"
        )
    
    # Создаём ответ
    answer = Answer(
        user_id=current_user.id,
        question_id=answer_data.question_id,
        date=datetime.utcnow(),
        text=answer_data.text
    )
    
    db.add(answer)
    db.commit()
    db.refresh(answer)
    
    return answer


@router.get("/answers", response_model=List[AnswerSchema])
def get_answers(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить ответы пользователя и партнёра"""
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
    query = db.query(Answer).filter(
        Answer.user_id.in_([current_user.id, partner_id])
    )
    
    if from_date:
        query = query.filter(db.func.date(Answer.date) >= from_date)
    
    if to_date:
        query = query.filter(db.func.date(Answer.date) <= to_date)
    
    answers = query.order_by(Answer.date.desc()).all()
    
    return answers
