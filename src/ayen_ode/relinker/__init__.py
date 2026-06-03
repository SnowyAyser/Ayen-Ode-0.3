from .parser import (
    text_needs_relinking,
    relink_text_programmatically,
    relink_text_with_llm,
    extract_investigate_tags,
    get_name_variants,
    get_all_linkable_entities,
)
from .pregenerator import (
    clear_pending_pregenerations,
    auto_pre_generate_new_investigations,
    pre_generate_scene_investigations_sync,
    queue_pregeneration,
)
from .db_relinker import run_database_relinking
from .history_relinker import relink_world_history_logs

__all__ = [
    "text_needs_relinking",
    "relink_text_programmatically",
    "relink_text_with_llm",
    "extract_investigate_tags",
    "get_name_variants",
    "get_all_linkable_entities",
    "clear_pending_pregenerations",
    "auto_pre_generate_new_investigations",
    "pre_generate_scene_investigations_sync",
    "queue_pregeneration",
    "run_database_relinking",
    "relink_world_history_logs",
]
