"""ArchMixin: backend database interactions for obligations/debts and intake logging."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, utc_now


class ArchMixin:
    """Service mixin for managing semantic obligations (debts) and intake logs."""

    # ------------------------------------------------------------------
    # World Debts (Quadruplets)
    # ------------------------------------------------------------------

    def record_debt(
        self,
        debtor_id: str,
        creditor_id: str,
        resource_type: str,
        quantity: str,
        detail: str,
        evidence: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Record a new financial, material, or moral debt in the world."""
        now = utc_now()
        debt_id = make_id("debt")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            # Validate entities exist in this world
            self._resolve_entity(conn, wid, debtor_id)
            self._resolve_entity(conn, wid, creditor_id)

            conn.execute(
                """
                INSERT INTO world_debts
                    (debt_id, world_id, debtor_id, creditor_id, resource_type, quantity, detail, status, evidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (debt_id, wid, debtor_id, creditor_id, resource_type.strip(), quantity.strip(), detail.strip(), "active", evidence.strip(), now, now),
            )

            # Return the created row as a dictionary
            row = conn.execute("SELECT * FROM world_debts WHERE debt_id = ?", (debt_id,)).fetchone()
            return self._debt_dict(conn, row)

    def update_debt_status(
        self,
        debt_id: str,
        status: str,
        detail: str = "",
        world: str | None = None,
    ) -> dict[str, Any]:
        """Resolve (satisfy) or default an active debt."""
        if status not in ("satisfied", "defaulted", "active"):
            raise ValueError("status must be satisfied, defaulted, or active")

        now = utc_now()
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            debt_row = conn.execute(
                "SELECT * FROM world_debts WHERE debt_id = ? AND world_id = ?",
                (debt_id, wid),
            ).fetchone()
            if not debt_row:
                raise ValueError(f"Debt not found: {debt_id}")

            update_detail = detail.strip() if detail else debt_row["detail"]

            conn.execute(
                """
                UPDATE world_debts
                SET status = ?, detail = ?, updated_at = ?
                WHERE debt_id = ? AND world_id = ?
                """,
                (status, update_detail, now, debt_id, wid),
            )

            row = conn.execute("SELECT * FROM world_debts WHERE debt_id = ?", (debt_id,)).fetchone()
            return self._debt_dict(conn, row)

    def list_active_debts(self, world: str | None = None) -> dict[str, Any]:
        """List all active debts in a given world."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            rows = conn.execute(
                """
                SELECT * FROM world_debts
                WHERE world_id = ? AND status = 'active'
                ORDER BY created_at DESC
                """,
                (wid,),
            ).fetchall()

            return {
                "world_id": wid,
                "debts": [self._debt_dict(conn, r) for r in rows],
            }

    def list_debt_history(self, world: str | None = None) -> dict[str, Any]:
        """List all resolved or defaulted debts in a given world."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            rows = conn.execute(
                """
                SELECT * FROM world_debts
                WHERE world_id = ? AND status != 'active'
                ORDER BY updated_at DESC
                """,
                (wid,),
            ).fetchall()

            return {
                "world_id": wid,
                "debts": [self._debt_dict(conn, r) for r in rows],
            }

    # ------------------------------------------------------------------
    # Intake Logger
    # ------------------------------------------------------------------

    def log_intake_run(
        self,
        narrative_text: str,
        thought_process: str,
        tools_attempted: list[dict[str, Any]],
        tools_executed: list[dict[str, Any]],
        game_time_label: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Record the full detailed report of a post-narration state extractor pass."""
        now = utc_now()
        log_id = make_id("ilog")
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            conn.execute(
                """
                INSERT INTO intake_logs
                    (log_id, world_id, narrative_text, thought_process, tools_attempted_json, tools_executed_json, game_time_label, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, wid, narrative_text.strip(), thought_process.strip(), dumps(tools_attempted), dumps(tools_executed), game_time_label.strip(), now),
            )

            row = conn.execute("SELECT * FROM intake_logs WHERE log_id = ?", (log_id,)).fetchone()
            return self._intake_log_dict(row)

    def list_intake_logs(self, limit: int = 20, world: str | None = None) -> dict[str, Any]:
        """Return the latest N post-narration logging records."""
        with self.connect() as conn:
            world_row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            wid = world_row["world_id"]

            rows = conn.execute(
                """
                SELECT * FROM intake_logs
                WHERE world_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (wid, limit),
            ).fetchall()

            return {
                "world_id": wid,
                "logs": [self._intake_log_dict(r) for r in rows],
            }

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _debt_dict(self, conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
        """Format a world_debts SQL row into a rich API dictionary, resolving entity names."""
        debtor_row = conn.execute("SELECT name, entity_type FROM entities WHERE entity_id = ?", (row["debtor_id"],)).fetchone()
        creditor_row = conn.execute("SELECT name, entity_type FROM entities WHERE entity_id = ?", (row["creditor_id"],)).fetchone()

        return {
            "debt_id": row["debt_id"],
            "world_id": row["world_id"],
            "debtor_id": row["debtor_id"],
            "debtor_name": debtor_row["name"] if debtor_row else "Unknown Entity",
            "debtor_type": debtor_row["entity_type"] if debtor_row else "character",
            "creditor_id": row["creditor_id"],
            "creditor_name": creditor_row["name"] if creditor_row else "Unknown Entity",
            "creditor_type": creditor_row["entity_type"] if creditor_row else "character",
            "resource_type": row["resource_type"],
            "quantity": row["quantity"],
            "detail": row["detail"],
            "status": row["status"],
            "evidence": row["evidence"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _intake_log_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Format an intake_logs SQL row into a dictionary, unpacking JSON payloads."""
        return {
            "log_id": row["log_id"],
            "world_id": row["world_id"],
            "narrative_text": row["narrative_text"],
            "thought_process": row["thought_process"],
            "tools_attempted": loads(row["tools_attempted_json"], []),
            "tools_executed": loads(row["tools_executed_json"], []),
            "game_time_label": row["game_time_label"],
            "created_at": row["created_at"],
        }
