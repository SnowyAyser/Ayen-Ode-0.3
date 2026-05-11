"""Quest routes: list, promote, dismiss, and check quest progress."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


def make_quest_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def list_quests(request: Request) -> JSONResponse:
        """GET /api/worlds/{world_id}/quests — return all quests for this world."""
        world_id = request.path_params["world_id"]
        tier = request.query_params.get("tier")
        status = request.query_params.get("status")
        try:
            data = service.list_quests(
                tier=int(tier) if tier else None,
                status=status or None,
                world=world_id,
            )
            return JSONResponse(data)
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    async def promote_quest(request: Request) -> JSONResponse:
        """POST /api/worlds/{world_id}/quests/{quest_id}/promote — pending_player → active."""
        world_id = request.path_params["world_id"]
        quest_id = request.path_params["quest_id"]
        try:
            quest = service.promote_quest(quest_id, world=world_id)
            return JSONResponse({"quest": quest})
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    async def dismiss_quest(request: Request) -> JSONResponse:
        """POST /api/worlds/{world_id}/quests/{quest_id}/dismiss — mark as dismissed."""
        world_id = request.path_params["world_id"]
        quest_id = request.path_params["quest_id"]
        try:
            quest = service.dismiss_quest(quest_id, world=world_id)
            return JSONResponse({"quest": quest})
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    async def check_quest(request: Request) -> JSONResponse:
        """POST /api/worlds/{world_id}/quests/{quest_id}/check — spend all points, return progress."""
        world_id = request.path_params["world_id"]
        quest_id = request.path_params["quest_id"]
        try:
            # Spend all investigation points
            currency = service.get_investigation_balance(world=world_id)
            balance = currency.get("balance", 0)
            if balance > 0:
                service.spend_investigation_points(balance, world=world_id)
            progress = service.check_quest_progress(quest_id, world=world_id)
            progress["points_spent"] = balance
            return JSONResponse(progress)
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    async def check_all_quests(request: Request) -> JSONResponse:
        """GET /api/worlds/{world_id}/quests/check-all — progress for every active quest (no cost)."""
        world_id = request.path_params["world_id"]
        try:
            quests_data = service.list_quests(
                status=None, world=world_id
            )
            results = []
            for q in quests_data.get("quests", []):
                if q["status"] in ("active", "pending_player"):
                    results.append(
                        service.check_quest_progress(q["quest_id"], world=world_id)
                    )
            return JSONResponse({"progress": results})
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    return [
        Route(
            "/api/worlds/{world_id}/quests",
            endpoint=list_quests,
            methods=["GET"],
        ),
        Route(
            "/api/worlds/{world_id}/quests/check-all",
            endpoint=check_all_quests,
            methods=["GET"],
        ),
        Route(
            "/api/worlds/{world_id}/quests/{quest_id}/promote",
            endpoint=promote_quest,
            methods=["POST"],
        ),
        Route(
            "/api/worlds/{world_id}/quests/{quest_id}/dismiss",
            endpoint=dismiss_quest,
            methods=["POST"],
        ),
        Route(
            "/api/worlds/{world_id}/quests/{quest_id}/check",
            endpoint=check_quest,
            methods=["POST"],
        ),
    ]
