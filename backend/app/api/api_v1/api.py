from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    pair,
    daily_question,
    mood,
    ritual,
    calendar,
    female_cycle,
    emotion_note,
    stats,
    export,
    account
)

api_router = APIRouter()

api_router.include_router(pair.router, prefix="/pair", tags=["pair"])
api_router.include_router(daily_question.router, prefix="/question", tags=["daily_question"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood"])
api_router.include_router(ritual.router, prefix="/rituals", tags=["ritual"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(female_cycle.router, prefix="/female", tags=["female_cycle"])
api_router.include_router(emotion_note.router, prefix="/notes", tags=["emotion_note"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
