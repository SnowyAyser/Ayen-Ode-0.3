import json
import threading
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..narrative import process_user_action, investigate_entity
from ..services.base import utc_now


def are_names_equivalent(a: str, b: str) -> bool:
    def strip_article(name: str) -> str:
        s = name.strip().lower()
        for art in ("the ", "a ", "an "):
            if s.startswith(art):
                return s[len(art):].strip()
        return s

    a_clean = strip_article(a)
    b_clean = strip_article(b)
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


def make_consequence_narrative_handlers(service, settings, sessions):
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
            matched_inv = next(
                (inv for inv in investigation_state.get("investigations", [])
                 if are_names_equivalent(inv["item_name"], item_name)),
                None
            )
            if matched_inv:
                currency = service.get_investigation_balance(world_id)
                return JSONResponse({
                    "world_id": world_id,
                    "investigation_id": f"completed_{matched_inv['item_name']}",
                    "item_name": matched_inv["item_name"],
                    "status": "complete",
                    "points_spent": 0,
                    "remaining_points": currency.get("balance", 0),
                    "success": True,
                    "already_completed": True,
                    "entity_id": matched_inv.get("entity_id")
                })
            active_queue = service.get_investigation_queue(world_id)
            
            # Check if already in queue
            job = next(
                (j for j in active_queue.get("jobs", []) if are_names_equivalent(j["entity_name"], item_name)),
                None
            )
            if job:
                if job["status"] == "queued":
                    service.prioritize_investigation_job_by_name(item_name, world_id)
                    updated_currency = service.get_investigation_balance(world_id)
                    return JSONResponse({
                        "world_id": world_id,
                        "investigation_id": job["job_id"],
                        "item_name": item_name,
                        "status": "queued",
                        "points_spent": 0,
                        "remaining_points": updated_currency.get("balance", 0),
                        "bumped": True,
                        "success": True,
                    })
                elif job["status"] == "processing":
                    updated_currency = service.get_investigation_balance(world_id)
                    return JSONResponse({
                        "world_id": world_id,
                        "investigation_id": job["job_id"],
                        "item_name": item_name,
                        "status": "processing",
                        "points_spent": 0,
                        "remaining_points": updated_currency.get("balance", 0),
                        "processing": True,
                        "success": True,
                    })

            currency = service.get_investigation_balance(world_id)
            if currency.get("balance", 0) < cost:
                return JSONResponse(
                    {"error": f"Insufficient investigation points: need {cost}, have {currency.get('balance', 0)}"},
                    status_code=400,
                )
            context = data.get("context", "")
            service.spend_investigation_points(cost, world=world_id)
            job = service.create_investigation_job(item_name, entity_type, cost=cost, context=context, world=world_id, priority=1)
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
            if result.get("status") == "processing":
                from ..narrative.stages.utils import get_stage_progress
                w_id = result.get("world_id")
                e_name = result.get("entity_name", "")
                progress_key = f"{w_id}:investigate:{e_name.lower()}"
                stage = get_stage_progress(progress_key)
                if stage:
                    result["active_stage"] = stage
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

            # Queue background pregeneration with high priority (0 = high)
            from ..relinker.pregenerator import queue_pregeneration
            queue_pregeneration(
                settings.anthropic_client,
                service,
                world_id,
                item_name,
                entity_type,
                priority=0,
                context=context
            )

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
            result = await run_sync(func)
            response = result[0]
            updated_history = result[1]
            theme_report = result[2]
            quest_report = result[3]
            mechanics_report = result[4]
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
                "theme_report": theme_report,
                "quest_report": quest_report,
                "mechanics_report": mechanics_report,
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def skip_time_handler(request: Request) -> JSONResponse:
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

    async def active_stage_handler(request: Request) -> JSONResponse:
        try:
            world_id = request.path_params.get("world_id")
            from ..narrative.stages.utils import get_stage_progress
            stage = get_stage_progress(world_id)
            return JSONResponse({"active_stage": stage})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def prioritize_handler(request: Request) -> JSONResponse:
        try:
            job_id = request.path_params.get("job_id")
            service.prioritize_investigation_job(job_id)
            return JSONResponse({"success": True, "job_id": job_id})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return {
        "investigate_handler": investigate_handler,
        "get_investigation_handler": get_investigation_handler,
        "pre_generate_investigation_handler": pre_generate_investigation_handler,
        "narrative_handler": narrative_handler,
        "skip_time_handler": skip_time_handler,
        "prioritize_handler": prioritize_handler,
        "active_stage_handler": active_stage_handler,
    }
