from starlette.requests import Request
from starlette.responses import JSONResponse

from ..context_assembler import ContextAssembler
from .auth import _client_ip


def make_consequence_handlers(service, settings, sessions):
    async def record_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.record_consequence(
                cause_id=data["cause_id"],
                effect_type=data["effect_type"],
                target_id=data["target_id"],
                detail=data.get("detail", ""),
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def record_chain_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            result = service.record_chain(
                cause_id=data["cause_id"],
                effects=data["effects"],
                world=world_id,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_effects_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            cause_id = request.query_params["cause_id"]
            result = service.get_effects(cause_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_causes_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            target_id = request.query_params["target_id"]
            result = service.get_causes(target_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def chain_forward_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            event_id = request.query_params["event_id"]
            depth = int(request.query_params.get("depth", 3))
            result = service.get_chain_forward(event_id, depth=depth, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def chain_backward_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.query_params["entity_id"]
            depth = int(request.query_params.get("depth", 3))
            result = service.get_chain_backward(entity_id, depth=depth, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def history_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            result = service.get_history(entity_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def state_at_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params["entity_id"]
            timestamp = request.query_params["timestamp"]
            result = service.get_state_at(entity_id, timestamp, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_events_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            cause_id = request.query_params.get("cause_id")
            target_id = request.query_params.get("target_id")
            effect_type = request.query_params.get("effect_type")
            limit = int(request.query_params.get("limit", 50))
            result = service.get_consequence_events(
                world=world_id, cause_id=cause_id, target_id=target_id,
                effect_type=effect_type, limit=limit,
            )
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def list_hooks_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            result = service.list_consequence_hooks(world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def register_hook_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            hook = service.register_consequence_hook(
                action_type=data["action_type"],
                action_params=data.get("action_params", {}),
                trigger_effect_type=data.get("trigger_effect_type"),
                trigger_cause_id=data.get("trigger_cause_id"),
                trigger_target_id=data.get("trigger_target_id"),
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
            result = service.remove_consequence_hook(hook_id=hook_id, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def context_packet_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            player_entity_id = request.query_params.get("player_entity_id")
            history_depth = int(request.query_params.get("history_depth", 10))
            tension_limit = int(request.query_params.get("tension_limit", 3))
            assembler = ContextAssembler(service)
            packet = assembler.assemble(
                world_id=world_id,
                player_entity_id=player_entity_id,
                history_depth=history_depth,
                tension_limit=tension_limit,
            )
            return JSONResponse({"success": True, "packet": packet})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def open_threads_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params.get("entity_id")
            limit = int(request.query_params.get("limit", 5))
            result = service.get_unresolved_threads(world=world_id, limit=limit)
            if entity_id:
                result["unresolved_threads"] = [
                    r for r in result["unresolved_threads"]
                    if r.get("cause_id") == entity_id or r.get("target_id") == entity_id
                ]
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    return {
        "record_handler": record_handler,
        "record_chain_handler": record_chain_handler,
        "get_effects_handler": get_effects_handler,
        "get_causes_handler": get_causes_handler,
        "chain_forward_handler": chain_forward_handler,
        "chain_backward_handler": chain_backward_handler,
        "history_handler": history_handler,
        "state_at_handler": state_at_handler,
        "get_events_handler": get_events_handler,
        "list_hooks_handler": list_hooks_handler,
        "register_hook_handler": register_hook_handler,
        "remove_hook_handler": remove_hook_handler,
        "context_packet_handler": context_packet_handler,
        "open_threads_handler": open_threads_handler,
    }
