"""World CRUD, initialization, and currency route handlers."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..narrative import initialize_world


def _assemble_world_data(service: Any, world_id: str | None) -> dict[str, Any]:
    """Resolve optional world_id and return world, handoff, and entity data."""
    if not world_id:
        active = service.get_active_world()
        if not active or not active.get("world"):
            raise ValueError("No active world")
        world_id = active["world"].get("world_id") or active["world"].get("id")
        if not world_id:
            raise ValueError("Could not determine world ID")
        world_status = service.get_world_status(world_id)
        world = world_status.get("world", active.get("world", {}))
    else:
        world_status = service.get_world_status(world_id)
        world = world_status.get("world", {})
    handoff = service.get_world_handoff(world_id)
    entities = service.list_entities(world=world_id)
    return {
        "success": True,
        "world_id": world_id,
        "world": world,
        "handoff": handoff.get("handoff", ""),
        "entities": entities.get("entities", []),
    }


def make_worlds_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def list_worlds_handler(request: Request) -> JSONResponse:
        try:
            include_archived = request.query_params.get("include_archived", "false").lower() == "true"
            result = service.list_worlds(include_archived=include_archived)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_active_world_handler(request: Request) -> JSONResponse:
        try:
            result = service.get_active_world()
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def switch_world_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id") or data.get("world")
            if not world_id:
                return JSONResponse({"error": "Missing world_id"}, status_code=400)
            result = service.switch_world(world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_world_status_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.query_params.get("world_id")
            result = service.get_world_status(world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def delete_world_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            result = service.delete_world(world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def reset_world_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            result = service.reset_world(world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_world_currencies_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            result = service.get_investigation_balance(world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def restore_world_currencies_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            data = await request.json()
            amount = int(data.get("amount", 1))
            result = service.restore_investigation_points(amount, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_world_time_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            result = service.get_world_time(world=world_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def skip_time_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            data = await request.json()
            seconds = int(data.get("seconds", 0))
            label = data.get("label", "")
            if seconds <= 0:
                return JSONResponse({"error": "seconds must be a positive integer"}, status_code=400)

            queue = service.get_investigation_queue(world=world_id)
            threads = service.get_unresolved_threads(world=world_id)
            blocking_jobs = queue.get("jobs", [])
            blocking_threads = threads.get("unresolved_threads", [])

            if blocking_jobs or blocking_threads:
                return JSONResponse(
                    {
                        "error": "Cannot skip time while events are still unfolding.",
                        "blocking": {
                            "investigation": [
                                {"name": j["entity_name"], "status": j["status"]}
                                for j in blocking_jobs
                            ],
                            "threads": [
                                {"effect_type": t["effect_type"], "detail": t.get("detail", "")}
                                for t in blocking_threads
                            ],
                        },
                    },
                    status_code=409,
                )

            result = service.advance_world_time(seconds=seconds, label=label, world=world_id)
            return JSONResponse({"success": True, "game_time": result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_world_data(request: Request) -> JSONResponse:
        try:
            world_id = request.query_params.get("world_id")
            return JSONResponse(_assemble_world_data(service, world_id))
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def create_and_init_world(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            name = data.get("name", "Untitled World")
            premise = data.get("premise", "")
            theme_tone = data.get("theme_tone", "")
            player_role = data.get("player_role", "")
            if not name or not premise:
                return JSONResponse({"error": "Missing name or premise"}, status_code=400)
            world_result = service.create_world(
                name=name,
                premise=premise,
                theme_tone=theme_tone,
                player_role=player_role,
                activate_now=True,
            )
            world_id = world_result.get("world", {}).get("world_id")
            if not world_id:
                return JSONResponse({"error": "Failed to create world"}, status_code=500)
            initial_scene = initialize_world(
                settings.anthropic_client,
                service,
                world_id,
                name,
                premise,
                theme_tone,
                player_role,
            )
            return JSONResponse({"world_id": world_id, "initial_scene": initial_scene, "success": True})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def init_world(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id")
            name = data.get("name", "Untitled World")
            premise = data.get("premise", "")
            theme_tone = data.get("theme_tone", "")
            player_role = data.get("player_role", "")
            if not world_id:
                return JSONResponse({"error": "Missing world_id"}, status_code=400)
            initial_scene = initialize_world(
                settings.anthropic_client,
                service,
                world_id,
                name,
                premise,
                theme_tone,
                player_role,
            )
            return JSONResponse({"world_id": world_id, "initial_scene": initial_scene, "success": True})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return [
        Route("/api/worlds", list_worlds_handler, methods=["GET"]),
        Route("/api/worlds/active", get_active_world_handler, methods=["GET"]),
        Route("/api/worlds/switch", switch_world_handler, methods=["POST"]),
        Route("/api/worlds/status", get_world_status_handler, methods=["GET"]),
        Route("/api/worlds/create", create_and_init_world, methods=["POST"]),
        Route("/api/worlds/init", init_world, methods=["POST"]),
        Route("/api/worlds/{world_id}", delete_world_handler, methods=["DELETE"]),
        Route("/api/worlds/{world_id}/reset", reset_world_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/currencies", get_world_currencies_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/currencies/restore", restore_world_currencies_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/time", get_world_time_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/skip-time", skip_time_handler, methods=["POST"]),
        Route("/api/world", get_world_data, methods=["GET"]),
    ]
