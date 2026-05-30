"""Consequence, investigation, narrative, and context-packet route handlers."""

from __future__ import annotations

import json
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..narrative import process_user_action, investigate_entity
from ..context_assembler import ContextAssembler
from ..services.base import utc_now


def are_names_equivalent(a: str, b: str) -> bool:
    a_clean = a.strip().lower()
    b_clean = b.strip().lower()
    if a_clean == b_clean:
        return True
    def get_variants(name: str):
        vars_set = {name}
        if name.endswith("s"):
            if name.endswith("es"):
                vars_set.add(name[:-2])
            vars_set.add(name[:-1])
        else:
            vars_set.add(name + "s")
            vars_set.add(name + "es")
        return vars_set
    return len(get_variants(a_clean).intersection(get_variants(b_clean))) > 0


def make_consequence_routes(service: Any, settings: Any, sessions: Any) -> list:
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

    async def investigate_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id")
            item_name = data.get("item_name", "")
            entity_type = data.get("entity_type", "object")
            cost = data.get("cost", 1)
            if not world_id or not item_name:
                return JSONResponse({"error": "Missing world_id or item_name"}, status_code=400)

            investigation_state = service.get_investigation_state(world_id)
            already_investigated = any(
                are_names_equivalent(inv["item_name"], item_name)
                for inv in investigation_state.get("investigations", [])
            )
            if already_investigated:
                return JSONResponse(
                    {"error": f"'{item_name}' has already been investigated"}, status_code=400
                )
            active_queue = service.get_investigation_queue(world_id)
            already_queued = any(
                are_names_equivalent(job["entity_name"], item_name)
                for job in active_queue.get("jobs", [])
            )
            if already_queued:
                return JSONResponse(
                    {"error": f"'{item_name}' is already under investigation"}, status_code=400
                )
            currency = service.get_investigation_balance(world_id)
            if currency.get("balance", 0) < cost:
                return JSONResponse(
                    {"error": f"Insufficient investigation points: need {cost}, have {currency.get('balance', 0)}"},
                    status_code=400,
                )
            context = data.get("context", "")
            service.spend_investigation_points(cost, world=world_id)
            job = service.create_investigation_job(item_name, entity_type, cost=cost, context=context, world=world_id)
            updated_currency = service.get_investigation_balance(world_id)
            return JSONResponse({
                "world_id": world_id,
                "investigation_id": job["job_id"],
                "item_name": item_name,
                "status": "queued",
                "points_spent": cost,
                "remaining_points": updated_currency.get("balance", 0),
                "success": True,
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def get_investigation_handler(request: Request) -> JSONResponse:
        try:
            job_id = request.path_params.get("job_id")
            result = service.get_investigation_job(job_id)
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def pre_generate_investigation_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id")
            item_name = data.get("item_name", "")
            entity_type = data.get("entity_type", "object")
            if not world_id or not item_name:
                return JSONResponse({"error": "Missing world_id or item_name"}, status_code=400)
            
            # 1. Check if already pre-generated in SQLite database (with singular/plural variants)
            with service.connect() as conn:
                cached_items = conn.execute(
                    "SELECT entity_name FROM pregenerated_investigations WHERE world_id = ?",
                    (world_id,),
                ).fetchall()
                for (cached_name,) in cached_items:
                    if are_names_equivalent(cached_name, item_name):
                        return JSONResponse({"success": True, "cached": True})

            # 2. Check if already in compendium/investigated (with singular/plural variants)
            investigation_state = service.get_investigation_state(world_id)
            already_investigated = any(
                are_names_equivalent(inv["item_name"], item_name)
                for inv in investigation_state.get("investigations", [])
            )
            if already_investigated:
                return JSONResponse({"success": True, "already_investigated": True})

            context = data.get("context", "")

            # Check if this item is already being pre-generated in a background thread
            from ..relinker import _pending_pregenerations, _pending_pregenerations_lock
            key = (world_id, item_name.strip().lower())
            with _pending_pregenerations_lock:
                if key in _pending_pregenerations:
                    return JSONResponse({"success": True, "cached": False, "status": "pending"})
                _pending_pregenerations.add(key)

            # 3. Offload Claude pre-generation and DB save to a background thread to prevent blocking
            def bg_pregenerate():
                try:
                    result = investigate_entity(
                        settings.anthropic_client,
                        service,
                        world_id,
                        item_name,
                        entity_type,
                        [],
                        save_to_db=False,
                        context=context
                    )
                    now = utc_now()
                    with service.connect() as conn:
                        conn.execute(
                            "INSERT OR REPLACE INTO pregenerated_investigations"
                            " (world_id, entity_name, entity_type, result_json, created_at)"
                            " VALUES (?, ?, ?, ?, ?)",
                            (world_id, item_name.strip(), entity_type.strip(), json.dumps(result), now),
                        )
                except Exception as ex:
                    print(f"Background pre-generation failed for {item_name}: {ex}")
                finally:
                    with _pending_pregenerations_lock:
                        _pending_pregenerations.discard(key)

            import threading
            thread = threading.Thread(target=bg_pregenerate, daemon=True)
            thread.start()

            return JSONResponse({"success": True, "cached": False})
        except Exception as e:
            print(f"Pre-generation error for {item_name}: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    async def narrative_handler(request: Request) -> JSONResponse:
        try:
            data = await request.json()
            world_id = data.get("world_id")
            user_action = data.get("action", "")
            history = data.get("history", [])
            player_entity_id = data.get("player_entity_id")
            if not world_id or not user_action:
                return JSONResponse({"error": "Missing world_id or action"}, status_code=400)
            import functools
            from anyio.to_thread import run_sync
            # Run blocking process_user_action in a separate worker thread to avoid blocking the event loop
            func = functools.partial(
                process_user_action,
                settings.anthropic_client,
                service,
                world_id,
                user_action,
                history,
                player_entity_id=player_entity_id,
            )
            response, updated_history = await run_sync(func)
            currency = service.restore_investigation_points(1, world=world_id)
            game_time = service.get_world_time(world=world_id)
            return JSONResponse({
                "world_id": world_id,
                "narrative": response,
                "history": updated_history,
                "investigation_points": currency["balance_after"],
                "max_investigation_points": currency["max_balance"],
                "game_time": {"seconds": game_time["seconds"], "label": game_time["label"]},
                "success": True,
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def open_threads_handler(request: Request) -> JSONResponse:
        """Return unresolved consequence threads for an entity or the whole world."""
        try:
            world_id = request.path_params["world_id"]
            entity_id = request.path_params.get("entity_id")
            limit = int(request.query_params.get("limit", 5))
            result = service.get_unresolved_threads(world=world_id, limit=limit)
            # Optionally narrow to threads involving this entity
            if entity_id:
                result["unresolved_threads"] = [
                    r for r in result["unresolved_threads"]
                    if r.get("cause_id") == entity_id or r.get("target_id") == entity_id
                ]
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def skip_time_handler(request: Request) -> JSONResponse:
        """Manually advance world time. Blocked if active investigation jobs exist.

        Body JSON: { "seconds": int, "label": str (optional) }
        """
        try:
            world_id = request.path_params["world_id"]
            # Guard: refuse if any investigation jobs are in progress
            queue = service.get_investigation_queue(world=world_id)
            if queue.get("jobs"):
                return JSONResponse(
                    {"error": "Cannot skip time while investigation jobs are active."},
                    status_code=409,
                )
            data = await request.json()
            seconds = int(data.get("seconds", 0))
            label = str(data.get("label", ""))
            if seconds <= 0:
                return JSONResponse({"error": "'seconds' must be a positive integer."}, status_code=400)
            result = service.advance_world_time(seconds=seconds, label=label, world=world_id)
            return JSONResponse({"success": True, **result})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    return [
        Route("/api/worlds/{world_id}/consequences", record_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/chain", record_chain_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/effects", get_effects_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/causes", get_causes_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/chain/forward", chain_forward_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/chain/backward", chain_backward_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/events", get_events_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/hooks", list_hooks_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/hooks", register_hook_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/consequences/hooks/{hook_id}", remove_hook_handler, methods=["DELETE"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/history", history_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/state-at", state_at_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/entities/{entity_id}/open-threads", open_threads_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/consequences/context-packet", context_packet_handler, methods=["GET"]),
        Route("/api/narrative", narrative_handler, methods=["POST"]),
        Route("/api/investigate", investigate_handler, methods=["POST"]),
        Route("/api/investigate/pre-generate", pre_generate_investigation_handler, methods=["POST"]),
        Route("/api/investigate/{job_id}", get_investigation_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/skip-time", skip_time_handler, methods=["POST"]),
    ]
