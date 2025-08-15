from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    pair,
    questions,
    mood,
    tune,
    tune_admin,
    ritual,
    calendar,
    female_cycle,
    emotion_note,
    stats,
    export,
    account,
    users,
    invitations,
    feedback,
    internal
)
from app.gpt import gpt_router
import app.api.api_v1.endpoints.announcements as announcements

api_router = APIRouter()

api_router.include_router(pair.router, prefix="/pair", tags=["pair"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood"])
api_router.include_router(tune.router, prefix="/tune", tags=["tune"])
api_router.include_router(tune_admin.router, prefix="/tune_admin", tags=["tune_admin"])
api_router.include_router(ritual.router, prefix="/rituals", tags=["ritual"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(female_cycle.router, prefix="/female", tags=["female_cycle"])
api_router.include_router(emotion_note.router, prefix="/notes", tags=["emotion_note"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(invitations.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["announcements"])
api_router.include_router(internal.router, prefix="/internal", tags=["internal"])
api_router.include_router(gpt_router, prefix="/gpt", tags=["gpt"])
