from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Iterable, Optional, Dict, Any, List
from datetime import timedelta

from app.models import User


class Trigger(Protocol):
    kind: str  # "event" | "schedule"


@dataclass
class ScheduledTrigger:
    cron: str  # для будущего, сейчас может быть строка описания
    kind: str = "schedule"


@dataclass
class EventTrigger:
    event_name: str
    kind: str = "event"


class Rule(Protocol):
    id: str
    trigger: Trigger
    priority: int

    def select_targets(self, ctx: Dict[str, Any]) -> Iterable[User]:
        ...

    def is_allowed(self, ctx: Dict[str, Any], user: User) -> bool:
        ...

    def cooldown(self) -> Optional[timedelta]:
        ...

    def make_dedupe(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        ...

    def render(self, ctx: Dict[str, Any], user: User) -> Dict[str, Any]:
        # returns {"text": str, "reply_markup": Optional[dict]}
        ...


_RULES: List[Rule] = []


def register_rule(rule: Rule) -> None:
    _RULES.append(rule)
    _RULES.sort(key=lambda r: getattr(r, "priority", 100))


def iter_rules(kind: str) -> Iterable[Rule]:
    for r in _RULES:
        if r.trigger.kind == kind:
            yield r