"""Knowledge graph route handlers."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


def make_knowledge_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def get_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_knowledge(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def known_by_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_known_by(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def by_degree_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            degree = request.path_params["degree"]
            result = service.get_knowledge_by_degree(entity_id, degree, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def shared_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_a = request.query_params["entity_a"]
            entity_b = request.query_params["entity_b"]
            result = service.get_shared_knowledge(entity_a, entity_b, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def chain_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.query_params["entity_id"]
            target_id = request.query_params["target_id"]
            result = service.get_knowledge_chain(entity_id, target_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def learn_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.learn(
                entity_id=data["entity_id"],
                target_id=data["target_id"],
                degree=data["degree"],
                source_id=data.get("source_id"),
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def spread_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.spread(
                knowledge_target_id=data["knowledge_target_id"],
                from_entity=data["from_entity"],
                to_entity=data["to_entity"],
                degree_decay=int(data.get("degree_decay", 1)),
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def forget_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.forget(
                entity_id=data["entity_id"],
                target_id=data["target_id"],
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def update_degree_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.update_degree(
                entity_id=data["entity_id"],
                target_id=data["target_id"],
                new_degree=data["new_degree"],
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def list_hooks_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            result = service.list_knowledge_hooks(world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def register_hook_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            hook = service.register_knowledge_hook(
                trigger_event_type=data["trigger_event_type"],
                action_type=data["action_type"],
                action_params=data.get("action_params", {}),
                trigger_entity_id=data.get("trigger_entity_id"),
                trigger_target_id=data.get("trigger_target_id"),
                trigger_degree=data.get("trigger_degree"),
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
            result = service.remove_knowledge_hook(hook_id=hook_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_events_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.query_params.get("entity_id")
            target_id = request.query_params.get("target_id")
            limit = int(request.query_params.get("limit", 50))
            result = service.get_knowledge_events(
                world=world_id, entity_id=entity_id, target_id=target_id, limit=limit
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_all_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            result = service.get_all_knowledge_links(world=world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    return [
        Route("/api/worlds/{world_id}/entities/{entity_id}/knowledge", get_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/known-by", known_by_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/knowledge/degree/{degree}", by_degree_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/knowledge/shared", shared_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/knowledge/chain", chain_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/knowledge/learn", learn_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/knowledge/spread", spread_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/knowledge/forget", forget_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/knowledge/degree", update_degree_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/knowledge/hooks", list_hooks_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/knowledge/hooks", register_hook_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/knowledge/hooks/{hook_id}", remove_hook_handler, methods=["DELETE"]),
        Route("/api/worlds/{world_id}/knowledge/events", get_events_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/knowledge/all", get_all_handler, methods=["GET"]),
    ]
