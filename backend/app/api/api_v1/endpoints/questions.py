from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import date, datetime, timedelta
import random
import httpx

from app.core.database import get_db
from app.models import User, Pair, Question, UserAnswer, UserQuestionStatus, PairDailyQuestion, QuestionNotification
from app.services.auth import get_current_user
from app.schemas.question import (
    QuestionResponse, 
    UserAnswerCreate, 
    UserAnswerResponse,
    QuestionStatusResponse,
    PairAnswersResponse
)
from app.core.config import settings
from app.services.notifications import NotificationService

router = APIRouter()


@router.get("/current", response_model=Optional[QuestionResponse])
async def get_current_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить вопрос дня для пары (один на пару в день).
    Если на сегодня ещё не назначен — назначаем первый неотвеченный обоими и возвращаем.
    Пользователь видит только назначенный на сегодня вопрос.
    """
    
    # Проверяем, есть ли у пользователя пара
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    
    if not user_pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас пока нет пары. Пригласите партнера!"
        )
    
    # Партнёр
    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id

    # Проверяем, назначен ли вопрос на сегодня для пары
    today = date.today()
    todays = db.query(PairDailyQuestion).filter(
        PairDailyQuestion.pair_id == user_pair.id,
        PairDailyQuestion.date == today
    ).first()

    if todays:
        q = db.query(Question).filter(Question.id == todays.question_id).first()
        user_answered = db.query(UserAnswer).filter(
            UserAnswer.user_id == current_user.id,
            UserAnswer.question_id == q.id
        ).first() is not None
        partner_answered = db.query(UserAnswer).filter(
            UserAnswer.user_id == partner_id,
            UserAnswer.question_id == q.id
        ).first() is not None
        return QuestionResponse(
            id=q.id,
            number=q.number,
            text=q.text,
            category=q.category,
            partner_answered=partner_answered,
            user_answered=user_answered
        )

    # Если на сегодня не назначен — найдём случайный вопрос, на который не ответили оба
    user_answered_ids = db.query(UserAnswer.question_id).filter(UserAnswer.user_id == current_user.id)
    partner_answered_ids = db.query(UserAnswer.question_id).filter(UserAnswer.user_id == partner_id)

    # Получаем все неотвеченные вопросы и выбираем случайный
    unanswered_questions = db.query(Question).filter(
        ~Question.id.in_(user_answered_ids),
        ~Question.id.in_(partner_answered_ids)
    ).all()
    
    if not unanswered_questions:
        return None
        
    # Выбираем случайный вопрос из неотвеченных
    next_question = random.choice(unanswered_questions)

    # Назначаем его как вопрос дня для пары
    assigned = PairDailyQuestion(
        pair_id=user_pair.id,
        question_id=next_question.id,
        date=today
    )
    db.add(assigned)
    db.commit()

    return QuestionResponse(
        id=next_question.id,
        number=next_question.number,
        text=next_question.text,
        category=next_question.category,
        partner_answered=False,
        user_answered=False
    )


@router.post("/answer", response_model=UserAnswerResponse)
async def submit_answer(
    answer_data: UserAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправить ответ на СЕГОДНЯШНИЙ вопрос пары. Нельзя отвечать на любой произвольный."""
    
    # Проверяем, существует ли вопрос
    question = db.query(Question).filter(Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вопрос не найден"
        )

    # Проверяем, что этот вопрос — назначенный на сегодня для пары
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()

    if not user_pair:
        raise HTTPException(status_code=404, detail="У вас пока нет пары")

    today = date.today()
    todays = db.query(PairDailyQuestion).filter(
        PairDailyQuestion.pair_id == user_pair.id,
        PairDailyQuestion.date == today,
        PairDailyQuestion.question_id == question.id
    ).first()
    if not todays:
        raise HTTPException(status_code=400, detail="Сегодня можно отвечать только на назначенный вопрос")
    
    # Проверяем, не отвечал ли пользователь уже на этот вопрос
    existing_answer = db.query(UserAnswer).filter(
        and_(
            UserAnswer.user_id == current_user.id,
            UserAnswer.question_id == answer_data.question_id
        )
    ).first()
    
    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже отвечали на этот вопрос"
        )
    
    # Создаем новый ответ
    new_answer = UserAnswer(
        user_id=current_user.id,
        question_id=answer_data.question_id,
        answer_text=answer_data.answer_text
    )
    
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    
    return UserAnswerResponse(
        id=new_answer.id,
        question_id=new_answer.question_id,
        answer_text=new_answer.answer_text,
        created_at=new_answer.created_at
    )


@router.get("/answers/{question_id}", response_model=PairAnswersResponse)
async def get_pair_answers(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить ответы пары на конкретный вопрос"""
    
    # Проверяем, существует ли вопрос
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вопрос не найден"
        )
    
    # Получаем пару пользователя
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    
    if not user_pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас пока нет пары"
        )
    
    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()
    
    # Получаем ответы пользователя и партнера
    user_answer = db.query(UserAnswer).filter(
        and_(
            UserAnswer.user_id == current_user.id,
            UserAnswer.question_id == question_id
        )
    ).first()
    
    partner_answer = db.query(UserAnswer).filter(
        and_(
            UserAnswer.user_id == partner_id,
            UserAnswer.question_id == question_id
        )
    ).first()
    
    # Пользователь может видеть ответ партнера только если сам ответил
    if not user_answer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Сначала ответьте на вопрос, чтобы увидеть ответ партнера"
        )
    
    return PairAnswersResponse(
        question=QuestionResponse(
            id=question.id,
            number=question.number,
            text=question.text,
            category=question.category,
            partner_answered=partner_answer is not None
        ),
        user_answer=UserAnswerResponse(
            id=user_answer.id,
            question_id=user_answer.question_id,
            answer_text=user_answer.answer_text,
            created_at=user_answer.created_at
        ) if user_answer else None,
        partner_answer=UserAnswerResponse(
            id=partner_answer.id,
            question_id=partner_answer.question_id,
            answer_text=partner_answer.answer_text,
            created_at=partner_answer.created_at
        ) if partner_answer else None,
        partner_name=partner.first_name if partner else "Партнер"
    )


@router.get("/history", response_model=List[QuestionStatusResponse])
async def get_questions_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """История: только вопросы, на которые текущий пользователь уже ответил (по ТЗ)."""
    
    # Получаем пару пользователя
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    
    if not user_pair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас пока нет пары"
        )
    
    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id
    
    # Только те вопросы, на которые ответил текущий пользователь
    answered_ids = db.query(UserAnswer.question_id).filter(UserAnswer.user_id == current_user.id)
    questions = db.query(Question).filter(Question.id.in_(answered_ids)).order_by(Question.number).offset(skip).limit(limit).all()
    
    result = []
    for question in questions:
        # Проверяем ответы пользователя и партнера
        user_answer = db.query(UserAnswer).filter(
            and_(
                UserAnswer.user_id == current_user.id,
                UserAnswer.question_id == question.id
            )
        ).first()
        
        partner_answer = db.query(UserAnswer).filter(
            and_(
                UserAnswer.user_id == partner_id,
                UserAnswer.question_id == question.id
            )
        ).first()
        
        result.append(QuestionStatusResponse(
            question=QuestionResponse(
                id=question.id,
                number=question.number,
                text=question.text,
                category=question.category,
                partner_answered=partner_answer is not None
            ),
            user_answered=user_answer is not None,
            partner_answered=partner_answer is not None,
            can_view_answers=user_answer is not None
        ))
    
    return result


@router.get("/stats")
async def get_questions_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить статистику по вопросам"""
    
    # Получаем пару пользователя
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    
    if not user_pair:
        return {
            "total_questions": 0,
            "user_answered": 0,
            "partner_answered": 0,
            "both_answered": 0,
            "completion_percentage": 0
        }
    
    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id
    
    # Общее количество вопросов
    total_questions = db.query(func.count(Question.id)).scalar()
    
    # Количество вопросов, на которые ответил пользователь
    user_answered = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == current_user.id
    ).scalar()
    
    # Количество вопросов, на которые ответил партнер
    partner_answered = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == partner_id
    ).scalar()
    
    # Количество вопросов, на которые ответили оба
    both_answered_query = db.query(UserAnswer.question_id).filter(
        UserAnswer.user_id == current_user.id
    ).intersect(
        db.query(UserAnswer.question_id).filter(
            UserAnswer.user_id == partner_id
        )
    )
    both_answered = len(both_answered_query.all())
    
    completion_percentage = (both_answered / total_questions * 100) if total_questions > 0 else 0
    
    return {
        "total_questions": total_questions,
        "user_answered": user_answered,
        "partner_answered": partner_answered,
        "both_answered": both_answered,
        "completion_percentage": round(completion_percentage, 1)
    }


@router.post("/notify_partner")
async def notify_partner_to_answer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправить партнёру уведомление в Telegram: «Партнёр ответил, можно отвечать».
    Доступно, если на сегодня назначен вопрос и текущий пользователь уже ответил, а партнёр — нет.
    """
    # Пара пользователя
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    if not user_pair:
        raise HTTPException(status_code=404, detail="У вас пока нет пары")

    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Партнёр не найден")

    # Назначенный на сегодня вопрос
    today = date.today()
    todays = db.query(PairDailyQuestion).filter(
        PairDailyQuestion.pair_id == user_pair.id,
        PairDailyQuestion.date == today
    ).first()
    if not todays:
        raise HTTPException(status_code=400, detail="На сегодня вопрос не назначен")

    question = db.query(Question).filter(Question.id == todays.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    # Проверяем ответы
    user_answer = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.question_id == question.id
    ).first()
    if not user_answer:
        raise HTTPException(status_code=400, detail="Сначала ответьте на вопрос")

    partner_answer = db.query(UserAnswer).filter(
        UserAnswer.user_id == partner_id,
        UserAnswer.question_id == question.id
    ).first()
    if partner_answer:
        return {"ok": True, "message": "Партнёр уже ответил"}

    # Проверяем, не отправляли ли мы уже уведомление за последний час
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_notification = db.query(QuestionNotification).filter(
        QuestionNotification.pair_id == user_pair.id,
        QuestionNotification.question_id == question.id,
        QuestionNotification.sender_user_id == current_user.id,
        QuestionNotification.recipient_user_id == partner_id,
        QuestionNotification.sent_at >= one_hour_ago
    ).first()
    
    if recent_notification:
        time_diff = datetime.utcnow() - recent_notification.sent_at
        minutes_left = 60 - int(time_diff.total_seconds() / 60)
        raise HTTPException(
            status_code=429, 
            detail=f"Уведомление уже отправлено. Попробуйте через {minutes_left} минут"
        )

    # Отправка сообщения через Telegram Bot API
    # Создаём диплинк на страницу вопросов
    webapp_base_url = settings.TELEGRAM_WEBAPP_URL or "https://gallery.homoludens.photos/pulse_of_pair/"
    webapp_url = f"{webapp_base_url}?tgWebAppStartParam=question_daily"

    text = (
        f"Ваш партнёр {current_user.first_name or ''} ответил на вопрос дня.\n"
        f"Откройте Пульс ваших отношений и ответьте тоже."
    ).strip()

    reply_markup = {
        "inline_keyboard": [[
            {"text": "Ответить на вопрос", "web_app": {"url": webapp_url}}
        ]]
    }

    service = NotificationService()
    await service.send(
        n_type="question_reminder",
        recipient=partner,
        text=text,
        reply_markup=reply_markup,
        pair=user_pair,
        actor=current_user,
        entity_type="question",
        entity_id=question.id,
        date_bucket=None,
        metadata={"source": "manual_notify"}
    )

    # Сохраняем запись об отправленном уведомлении
    notification_record = QuestionNotification(
        pair_id=user_pair.id,
        question_id=question.id,
        sender_user_id=current_user.id,
        recipient_user_id=partner_id
    )
    db.add(notification_record)
    db.commit()

    return {"ok": True}
