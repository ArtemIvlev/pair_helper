from fastapi import APIRouter

router = APIRouter()

@router.get("/participation")
def get_participation_stats():
    """Получить статистику участия"""
    return {"message": "Статистика участия - в разработке"}

@router.get("/mood-trend")
def get_mood_trend():
    """Получить тренд настроений"""
    return {"message": "Тренд настроений - в разработке"}
