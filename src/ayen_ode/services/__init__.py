"""Assembles AyenOdeService from domain-specific mixin classes."""

from .base import BaseService
from .worlds import WorldsMixin
from .entities import EntitiesMixin
from .stats import StatsMixin
from .containment import ContainmentMixin
from .knowledge import KnowledgeMixin
from .consequence import ConsequenceMixin
from .investigation import InvestigationMixin
from .sync import SyncMixin
from .quests import QuestsMixin
from .arch import ArchMixin


class AyenOdeService(
    WorldsMixin,
    EntitiesMixin,
    StatsMixin,
    ContainmentMixin,
    KnowledgeMixin,
    ConsequenceMixin,
    InvestigationMixin,
    SyncMixin,
    QuestsMixin,
    ArchMixin,
    BaseService,
):
    """SQLite-backed state service for Ayen-Ode, composed from domain mixins.

    MRO: WorldsMixin, EntitiesMixin, StatsMixin, ContainmentMixin,
    KnowledgeMixin, ConsequenceMixin, InvestigationMixin, SyncMixin,
    QuestsMixin, ArchMixin, BaseService.

    BaseService provides: __init__, connect(), initialize(), and all shared
    private helpers (_resolve_world, _entity_stats, _world_dict, etc.).
    """


__all__ = ["AyenOdeService"]