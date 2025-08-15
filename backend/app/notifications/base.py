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


# Registry для правил
_RULES: Dict[str, list[Rule]] = {"schedule": [], "event": []}


def msk_to_utc_cron(hour: int, minute: int = 0) -> str:
    """
    Конвертирует московское время в UTC cron выражение.
    MSK = UTC + 3, поэтому UTC = MSK - 3
    """
    utc_hour = (hour - 3) % 24  # MSK - 3, с учетом перехода через полночь
    return f"{minute} {utc_hour} * * *"


def register_rule(rule: Rule) -> None:
    """Регистрирует правило в соответствующей категории"""
    if isinstance(rule.trigger, ScheduledTrigger):
        _RULES["schedule"].append(rule)
    elif isinstance(rule.trigger, EventTrigger):
        _RULES["event"].append(rule)


def iter_rules(kind: str) -> Iterable[Rule]:
    """Итерирует по правилам указанного типа"""
    return _RULES.get(kind, [])


