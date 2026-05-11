"""Entity CRUD and linking route handlers."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


def make_entities_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def list_entities_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.query_params.get("world_id")
            entity_type = request.query_params.get("entity_type")
            include_archived = request.query_params.get("include_archived", "false").lower() == "true"
            result = service.list_entities(world=world_id, entity_type=entity_type, include_archived=include_archived)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_entity_handler(request: Request) -> JSONResponse:
        try:
            entity_id = request.path_params.get("entity_id")
            world_id = request.query_params.get("world_id")
            result = service.get_entity(entity_id, world=world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_entity_stats_handler(request: Request) -> JSONResponse:
        try:
            entity_id = request.path_params.get("entity_id")
            world_id = request.query_params.get("world_id")
            result = service.get_entity_stats(entity_id, world=world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def link_entities_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id")
            entity_id_a = data.get("entity_id_a")
            entity_id_b = data.get("entity_id_b")
            relation = data.get("relation", "")
            if not world_id or not entity_id_a or not entity_id_b:
                return JSONResponse(
                    {"error": "Missing world_id, entity_id_a, or entity_id_b"}, status_code=400
                )
            result = service.link_entities(entity_id_a, entity_id_b, world=world_id, relation=relation)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return [
        Route("/api/entities", list_entities_handler, methods=["GET"]),
        Route("/api/entities/link", link_entities_handler, methods=["POST"]),
        Route("/api/entities/{entity_id}", get_entity_handler, methods=["GET"]),
        Route("/api/entities/{entity_id}/stats", get_entity_stats_handler, methods=["GET"]),
    ]
