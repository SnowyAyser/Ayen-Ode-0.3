from typing import Any
from starlette.routing import Route

from .consequence_handlers import make_consequence_handlers
from .consequence_narrative import make_consequence_narrative_handlers


def make_consequence_routes(service: Any, settings: Any, sessions: Any) -> list:
    h = make_consequence_handlers(service, settings, sessions)
    n = make_consequence_narrative_handlers(service, settings, sessions)

    return [
        Route("/api/worlds/{world_id}/consequences", h["record_handler"], methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/chain", h["record_chain_handler"], methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/effects", h["get_effects_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/causes", h["get_causes_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/chain/forward", h["chain_forward_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/chain/backward", h["chain_backward_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/events", h["get_events_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/hooks", h["list_hooks_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/hooks", h["register_hook_handler"], methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/hooks/{hook_id}", h["remove_hook_handler"], methods=["DELETE"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/history", h["history_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/state-at", h["state_at_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/open-threads", h["open_threads_handler"], methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/context-packet", h["context_packet_handler"], methods=["GET"]),
        Route("/api/narrative", n["narrative_handler"], methods=["POST"]),
        Route("/api/worlds/{world_id}/active-stage", n["active_stage_handler"], methods=["GET"]),
        Route("/api/investigate", n["investigate_handler"], methods=["POST"]),
        Route("/api/investigate/pre-generate", n["pre_generate_investigation_handler"], methods=["POST"]),
        Route("/api/investigate/{job_id}", n["get_investigation_handler"], methods=["GET"]),
        Route("/api/investigate/{job_id}/prioritize", n["prioritize_handler"], methods=["POST"]),
        Route("/api/worlds/{world_id}/skip-time", n["skip_time_handler"], methods=["POST"]),
    ]
