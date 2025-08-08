from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_rituals():
    """Получить список ритуалов пары"""
    return {"message": "Ритуалы - в разработке"}

@router.post("/")
def create_ritual():
    """Создать/редактировать ритуал"""
    return {"message": "Создание ритуала - в разработке"}

@router.post("/check")
def check_ritual():
    """Отметить выполнение ритуала"""
    return {"message": "Отметка выполнения - в разработке"}
