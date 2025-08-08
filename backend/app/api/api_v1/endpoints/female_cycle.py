from fastapi import APIRouter

router = APIRouter()

@router.get("/cycle")
def get_female_cycle():
    """Получить параметры цикла"""
    return {"message": "Женский цикл - в разработке"}

@router.post("/cycle")
def create_female_cycle():
    """Задать параметры цикла"""
    return {"message": "Создание цикла - в разработке"}

@router.post("/cycle/log")
def create_cycle_log():
    """Добавить симптом/заметку"""
    return {"message": "Лог цикла - в разработке"}
