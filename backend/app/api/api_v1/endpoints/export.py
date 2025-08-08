from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def export_data():
    """Экспорт данных пользователя"""
    return {"message": "Экспорт данных - в разработке"}
