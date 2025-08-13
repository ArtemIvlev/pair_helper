from __future__ import annotations

from typing import Dict, Any

from app.models import User
from app.core.database import SessionLocal
from app.services.notifications import NotificationService
from .base import iter_rules


class NotificationEngine:
    def __init__(self, service: NotificationService | None = None) -> None:
        self.service = service or NotificationService()

    async def run_scheduled(self, ctx: Dict[str, Any]) -> None:
        async def handle_rule(rule, user: User):
            if not rule.is_allowed(ctx, user):
                return
            dedupe = rule.make_dedupe(ctx, user)
            render = rule.render(ctx, user)
            await self.service.send(
                n_type=rule.id,
                recipient=user,
                text=render.get("text", ""),
                reply_markup=render.get("reply_markup"),
                pair=ctx.get("pair"),
                actor=ctx.get("actor"),
                entity_type=dedupe.get("entity_type"),
                entity_id=dedupe.get("entity_id"),
                date_bucket=dedupe.get("date_bucket"),
                cooldown=rule.cooldown(),
                metadata=render.get("meta") or {},
            )

        for rule in iter_rules("schedule"):
            for user in rule.select_targets(ctx):
                await handle_rule(rule, user)

    async def handle_event(self, event_name: str, ctx: Dict[str, Any]) -> None:
        for rule in iter_rules("event"):
            if getattr(rule.trigger, "event_name", None) != event_name:
                continue
            for user in rule.select_targets(ctx):
                if not rule.is_allowed(ctx, user):
                    continue
                dedupe = rule.make_dedupe(ctx, user)
                render = rule.render(ctx, user)
                await self.service.send(
                    n_type=rule.id,
                    recipient=user,
                    text=render.get("text", ""),
                    reply_markup=render.get("reply_markup"),
                    pair=ctx.get("pair"),
                    actor=ctx.get("actor"),
                    entity_type=dedupe.get("entity_type"),
                    entity_id=dedupe.get("entity_id"),
                    date_bucket=dedupe.get("date_bucket"),
                    cooldown=rule.cooldown(),
                    metadata=render.get("meta") or {},
                )