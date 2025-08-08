from fastapi import APIRouter

router = APIRouter()

@router.post("/delete")
def delete_account():
    """Полное удаление аккаунта"""
    return {"message": "Удаление аккаунта - в разработке"}
