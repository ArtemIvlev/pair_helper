from datetime import date
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.core.database import get_db
from app.models import User, Pair
from app.models.tune import PairDailyTuneQuestion, TuneAnswer, TuneQuizQuestion
from app.services.auth import get_current_user
from app.schemas.tune import (
    TuneQuestionResponse,
    TuneAnswerCreate,
    TunePairAnswersResponse,
    TuneAnswerItem,
)


router = APIRouter()


@router.get("/current", response_model=Optional[TuneQuestionResponse])
def get_current_tune_question(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить вопрос дня (Сонастройка) для пары. Если не назначен — назначить случайный неотвеченный обоими.
    Возвращает вопрос и флаги по 4 ответам относительно текущего пользователя.
    """
    # Пара
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    if not user_pair:
        raise HTTPException(status_code=404, detail="У вас пока нет пары. Пригласите партнера!")

    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id

    # Назначен ли на сегодня вопрос
    today = date.today()
    todays = db.query(PairDailyTuneQuestion).filter(
        PairDailyTuneQuestion.pair_id == user_pair.id,
        PairDailyTuneQuestion.date == today
    ).first()

    if not todays:
        # Соберем вопросы, полностью закрытые (есть 4 уникальные комбинации ответов для пары)
        sub_completed_q = (
            db.query(TuneAnswer.question_id)
            .filter(TuneAnswer.pair_id == user_pair.id)
            .group_by(TuneAnswer.question_id)
            .having(func.count(TuneAnswer.id) >= 4)
        )

        # Используем только специальные вопросы для квиза Сонастройка
        candidates = db.query(TuneQuizQuestion).filter(~TuneQuizQuestion.id.in_(sub_completed_q)).all()
        if not candidates:
            return None
        chosen = random.choice(candidates)
        todays = PairDailyTuneQuestion(pair_id=user_pair.id, question_id=chosen.id, date=today)

        db.add(todays)
        db.commit()

    # Получаем вопрос квиза Сонастройка
    quiz = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == todays.question_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Вопрос квиза не найден")
    
    q_id, q_number, q_text, q_category = quiz.id, (quiz.number or 0), (quiz.text or ''), quiz.category
    options = (quiz.option1, quiz.option2, quiz.option3, quiz.option4)
    q_type = quiz.question_type or "mcq"
    text_about_partner = quiz.text_about_partner
    text_about_self = quiz.text_about_self

    # Флаги выполненных ответов (4 комбинации)
    me_about_me = db.query(TuneAnswer).filter(
        TuneAnswer.pair_id == user_pair.id,
        TuneAnswer.question_id == q_id,
        TuneAnswer.author_user_id == current_user.id,
        TuneAnswer.subject_user_id == current_user.id
    ).first() is not None

    me_about_partner = db.query(TuneAnswer).filter(
        TuneAnswer.pair_id == user_pair.id,
        TuneAnswer.question_id == q_id,
        TuneAnswer.author_user_id == current_user.id,
        TuneAnswer.subject_user_id == partner_id
    ).first() is not None

    partner_about_partner = db.query(TuneAnswer).filter(
        TuneAnswer.pair_id == user_pair.id,
        TuneAnswer.question_id == q_id,
        TuneAnswer.author_user_id == partner_id,
        TuneAnswer.subject_user_id == partner_id
    ).first() is not None

    partner_about_me = db.query(TuneAnswer).filter(
        TuneAnswer.pair_id == user_pair.id,
        TuneAnswer.question_id == q_id,
        TuneAnswer.author_user_id == partner_id,
        TuneAnswer.subject_user_id == current_user.id
    ).first() is not None

    return TuneQuestionResponse(
        id=q_id,
        number=q_number,
        text=q_text,
        category=q_category,
        question_type=q_type,
        option1=options[0],
        option2=options[1],
        option3=options[2],
        option4=options[3],
        text_about_partner=text_about_partner,
        text_about_self=text_about_self,
        me_about_me=me_about_me,
        me_about_partner=me_about_partner,
        partner_about_partner=partner_about_partner,
        partner_about_me=partner_about_me,
    )


@router.post("/answer", response_model=TuneAnswerItem)
def submit_tune_answer(
    payload: TuneAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправить ответ в режиме Сонастройки. about: me|partner."""
    # Пара
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    if not user_pair:
        raise HTTPException(status_code=404, detail="У вас пока нет пары")

    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id

    # Проверяем, что вопрос существует (только квиз Сонастройка)
    quiz = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == payload.question_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Вопрос квиза не найден")

    # Проверяем, что этот вопрос назначен сегодня для пары
    today = date.today()
    todays = db.query(PairDailyTuneQuestion).filter(
        PairDailyTuneQuestion.pair_id == user_pair.id,
        PairDailyTuneQuestion.date == today,
        PairDailyTuneQuestion.question_id == payload.question_id
    ).first()
    if not todays:
        raise HTTPException(status_code=400, detail="Сегодня можно отвечать только на назначенный вопрос")

    # Определяем субъект ответа
    subject_user_id = current_user.id if payload.about == "me" else partner_id

    # Проверяем дубликат по уникальному набору
    existing = db.query(TuneAnswer).filter(
        and_(
            TuneAnswer.pair_id == user_pair.id,
            TuneAnswer.question_id == payload.question_id,
            TuneAnswer.author_user_id == current_user.id,
            TuneAnswer.subject_user_id == subject_user_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вы уже ответили по этой комбинации")

    # Формируем ответ: для MCQ используем selected_option, иначе answer_text
    answer_kwargs = dict(
        pair_id=user_pair.id,
        question_id=payload.question_id,
        author_user_id=current_user.id,
        subject_user_id=subject_user_id,
    )
    # Для квиза Сонастройка используем только MCQ
    if payload.selected_option is None:
        raise HTTPException(status_code=400, detail="Не выбран вариант ответа")
    answer_kwargs.update(answer_text=str(payload.selected_option), selected_option=payload.selected_option)

    answer = TuneAnswer(**answer_kwargs)
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return answer


@router.get("/answers/{question_id}", response_model=TunePairAnswersResponse)
def get_tune_answers(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все 4 ответа по вопросу Сонастройки для пары. Доступно обоим."""
    # Пара
    user_pair = db.query(Pair).filter(
        or_(Pair.user1_id == current_user.id, Pair.user2_id == current_user.id)
    ).first()
    if not user_pair:
        raise HTTPException(status_code=404, detail="У вас пока нет пары")

    partner_id = user_pair.user2_id if user_pair.user1_id == current_user.id else user_pair.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()

    # Получаем вопрос квиза Сонастройка
    quiz = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == question_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Вопрос квиза не найден")
    
    q_id, q_number, q_text, q_category = quiz.id, (quiz.number or 0), (quiz.text or ''), quiz.category
    options = (quiz.option1, quiz.option2, quiz.option3, quiz.option4)
    q_type = quiz.question_type or "mcq"
    text_about_partner = quiz.text_about_partner
    text_about_self = quiz.text_about_self

    answers_raw = db.query(TuneAnswer).filter(
        TuneAnswer.pair_id == user_pair.id,
        TuneAnswer.question_id == question_id,
    ).order_by(TuneAnswer.created_at.asc()).all()

    # Анализируем ответы и формируем статус
    me_answers = None
    partner_answers = None
    
    if answers_raw:
        # Находим мои ответы
        my_about_me = next((a for a in answers_raw if a.author_user_id == current_user.id and a.subject_user_id == current_user.id), None)
        my_about_partner = next((a for a in answers_raw if a.author_user_id == current_user.id and a.subject_user_id == partner_id), None)
        
        if my_about_me or my_about_partner:
            me_answers = {
                "about_me": int(my_about_me.answer_text) if my_about_me else None,
                "about_partner": int(my_about_partner.answer_text) if my_about_partner else None
            }
        
        # Находим ответы партнера
        partner_about_himself = next((a for a in answers_raw if a.author_user_id == partner_id and a.subject_user_id == partner_id), None)
        partner_about_me = next((a for a in answers_raw if a.author_user_id == partner_id and a.subject_user_id == current_user.id), None)
        
        if partner_about_himself or partner_about_me:
            partner_answers = {
                "about_himself": int(partner_about_himself.answer_text) if partner_about_himself else None,
                "about_me": int(partner_about_me.answer_text) if partner_about_me else None
            }

    return TunePairAnswersResponse(
        question=TuneQuestionResponse(
            id=q_id,
            number=q_number,
            text=q_text,
            category=q_category,
            question_type=q_type,
            option1=options[0], option2=options[1], option3=options[2], option4=options[3],
            text_about_partner=text_about_partner,
            text_about_self=text_about_self
        ),
        partner_name=partner.first_name if partner else "Партнер",
        me=me_answers,
        partner=partner_answers
    )


