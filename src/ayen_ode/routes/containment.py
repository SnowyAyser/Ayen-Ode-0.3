"""Containment tree route handlers."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


def make_containment_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def get_contents_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_contents(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_contents_recursive_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_contents_recursive(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_container_chain_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_container_chain(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_siblings_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_siblings(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def move_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.move(
                entity_id=data["entity_id"],
                new_container_id=data.get("new_container_id"),
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def list_hooks_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            container_id = request.query_params.get("container_id")
            result = service.list_containment_hooks(world=world_id, container_id=container_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def register_hook_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            hook = service.register_containment_hook(
                trigger_event_type=data["trigger_event_type"],
                action_type=data["action_type"],
                action_params=data.get("action_params", {}),
                trigger_container_id=data.get("trigger_container_id"),
                trigger_entity_id=data.get("trigger_entity_id"),
                label=data.get("label", ""),
                world=world_id,
            )
            return JSONResponse({"success": True, "hook": hook})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def remove_hook_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            hook_id = request.path_params["hook_id"]
            result = service.remove_containment_hook(hook_id=hook_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_events_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.query_params.get("entity_id")
            container_id = request.query_params.get("container_id")
            limit = int(request.query_params.get("limit", 50))
            result = service.get_containment_events(
                world=world_id, entity_id=entity_id, container_id=container_id, limit=limit
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    return [
        Route("/api/worlds/{world_id}/entities/{entity_id}/contents", get_contents_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/contents/recursive", get_contents_recursive_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/container-chain", get_container_chain_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/siblings", get_siblings_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/containment/move", move_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/containment/hooks", list_hooks_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/containment/hooks", register_hook_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/containment/hooks/{hook_id}", remove_hook_handler, methods=["DELETE"]),
        Route("/api/worlds/{world_id}/containment/events", get_events_handler, methods=["GET"]),
    ]
