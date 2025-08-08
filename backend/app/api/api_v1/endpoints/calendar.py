from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_calendar_events():
    """Получить события календаря"""
    return {"message": "Календарь - в разработке"}

@router.post("/")
def create_calendar_event():
    """Создать/редактировать событие"""
    return {"message": "Создание события - в разработке"}
