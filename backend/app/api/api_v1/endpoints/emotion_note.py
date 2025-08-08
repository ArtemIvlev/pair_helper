from fastapi import APIRouter

router = APIRouter()

@router.post("/emotion")
def create_emotion_note():
    """Создать эмоциональную заметку"""
    return {"message": "Эмоциональные заметки - в разработке"}
