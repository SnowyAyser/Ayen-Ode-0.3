"""REST API routes for managing obligations/debts and viewing intake logs."""

from __future__ import annotations

from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


def make_arch_routes(service: Any, settings: Any, sessions: Any) -> list:
    async def get_debts_handler(request: Request) -> JSONResponse:
        """Fetch all active and history debts in the world."""
        try:
            world_id = request.path_params["world_id"]
            active_res = service.list_active_debts(world=world_id)
            history_res = service.list_debt_history(world=world_id)
            return JSONResponse({
                "success": True,
                "world_id": world_id,
                "active": active_res.get("debts", []),
                "history": history_res.get("debts", []),
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def create_debt_handler(request: Request) -> JSONResponse:
        """Manually assert a custom debt (override)."""
        try:
            world_id = request.path_params["world_id"]
            data = await request.json()
            debt = service.record_debt(
                debtor_id=data["debtor_id"],
                creditor_id=data["creditor_id"],
                resource_type=data["resource_type"],
                quantity=data["quantity"],
                detail=data.get("detail", ""),
                evidence=data.get("evidence", "Manual developer override assertion"),
                world=world_id,
            )
            return JSONResponse({"success": True, "debt": debt})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def update_debt_status_handler(request: Request) -> JSONResponse:
        """Manually resolve or default an active debt."""
        try:
            world_id = request.path_params["world_id"]
            debt_id = request.path_params["debt_id"]
            data = await request.json()
            status = data["status"]
            detail = data.get("detail", "")
            debt = service.update_debt_status(
                debt_id=debt_id,
                status=status,
                detail=detail,
                world=world_id,
            )
            return JSONResponse({"success": True, "debt": debt})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    async def get_intake_logs_handler(request: Request) -> JSONResponse:
        """Retrieve recent post-narration state extractor logs."""
        try:
            world_id = request.path_params["world_id"]
            limit = int(request.query_params.get("limit", 20))
            logs_res = service.list_intake_logs(limit=limit, world=world_id)
            return JSONResponse({
                "success": True,
                "world_id": world_id,
                "logs": logs_res.get("logs", []),
            })
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)

    return [
        Route("/api/worlds/{world_id}/arch/debts", get_debts_handler, methods=["GET"]),
        Route("/api/worlds/{world_id}/arch/debts", create_debt_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/arch/debts/{debt_id}/status", update_debt_status_handler, methods=["POST"]),
        Route("/api/worlds/{world_id}/arch/intake-logs", get_intake_logs_handler, methods=["GET"]),
    ]
