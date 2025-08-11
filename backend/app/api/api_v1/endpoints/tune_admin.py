from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tune import TuneQuizQuestion, TuneQuestionType
from app.schemas.tune import TuneQuizQuestionCreate, TuneQuizQuestion


router = APIRouter()


@router.get("/", response_model=list[TuneQuizQuestion])
def list_quiz_questions(db: Session = Depends(get_db)):
    items = db.query(TuneQuizQuestion).order_by(TuneQuizQuestion.number.nulls_last(), TuneQuizQuestion.id).all()
    return items


@router.post("/", response_model=TuneQuizQuestion)
def create_quiz_question(payload: TuneQuizQuestionCreate, db: Session = Depends(get_db)):
    if payload.question_type == 'mcq':
        # Проверим, что все 4 варианта есть (минимум 2 — но по ТЗ 4)
        opts = [payload.option1, payload.option2, payload.option3, payload.option4]
        if any(o is None or not str(o).strip() for o in opts):
            raise HTTPException(status_code=400, detail="Для MCQ нужно 4 варианта ответа")

    item = TuneQuizQuestion(
        number=payload.number,
        text=payload.text,
        category=payload.category,
        question_type=TuneQuestionType.MCQ if payload.question_type == 'mcq' else TuneQuestionType.TEXT,
        option1=payload.option1,
        option2=payload.option2,
        option3=payload.option3,
        option4=payload.option4,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=TuneQuizQuestion)
def update_quiz_question(item_id: int, payload: TuneQuizQuestionCreate, db: Session = Depends(get_db)):
    item = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    if payload.question_type == 'mcq':
        opts = [payload.option1, payload.option2, payload.option3, payload.option4]
        if any(o is None or not str(o).strip() for o in opts):
            raise HTTPException(status_code=400, detail="Для MCQ нужно 4 варианта ответа")

    item.number = payload.number
    item.text = payload.text
    item.category = payload.category
    item.question_type = TuneQuestionType.MCQ if payload.question_type == 'mcq' else TuneQuestionType.TEXT
    item.option1 = payload.option1
    item.option2 = payload.option2
    item.option3 = payload.option3
    item.option4 = payload.option4

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_quiz_question(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TuneQuizQuestion).filter(TuneQuizQuestion.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    db.delete(item)
    db.commit()
    return {"ok": True}


