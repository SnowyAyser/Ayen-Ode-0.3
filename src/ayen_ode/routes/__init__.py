"""Route factory package — assembles all Starlette routes."""

from __future__ import annotations

from typing import Any

from .auth import make_auth_routes
from .worlds import make_worlds_routes
from .entities import make_entities_routes
from .containment import make_containment_routes
from .knowledge import make_knowledge_routes
from .consequence import make_consequence_routes
from .quests import make_quest_routes
from .arch import make_arch_routes


def make_all_routes(service: Any, settings: Any, sessions: Any) -> list:
    return (
        make_auth_routes(service, settings, sessions)
        + make_worlds_routes(service, settings, sessions)
        + make_entities_routes(service, settings, sessions)
        + make_containment_routes(service, settings, sessions)
        + make_knowledge_routes(service, settings, sessions)
        + make_consequence_routes(service, settings, sessions)
        + make_quest_routes(service, settings, sessions)
        + make_arch_routes(service, settings, sessions)
    )
