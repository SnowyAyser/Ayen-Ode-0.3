"""InvestigationMixin: investigation jobs, state tracking, and points currency."""

from __future__ import annotations

from typing import Any
import sqlite3

from .base import dumps, loads, make_id, utc_now


class InvestigationMixin:
    """Async investigation jobs, investigation state history, and points currency."""

    # --- Currency ---

    def initialize_world_currency(
        self,
        world: str | None = None,
        initial_balance: int = 5,
        max_balance: int = 5,
    ) -> dict[str, Any]:
        """Set up investigation points currency for a world."""
        now = utc_now()
        world_id = None
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            world_id = row["world_id"]
            conn.execute(
                """
                INSERT OR IGNORE INTO world_currencies
                (currency_id, world_id, currency_type, current_balance, max_balance, last_regen_at, regen_rate)
                VALUES (?, ?, 'investigation_points', ?, ?, ?, 0)
                """,
                (make_id("currency"), world_id, initial_balance, max_balance, now),
            )
        return self.get_investigation_balance(world_id)

    def get_investigation_balance(self, world: str | None = None) -> dict[str, Any]:
        """Get investigation points balance for a world."""
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            currency = conn.execute(
                "SELECT * FROM world_currencies WHERE world_id = ?",
                (row["world_id"],),
            ).fetchone()
            if not currency:
                return {"world_id": row["world_id"], "balance": 0, "max_balance": 0, "error": "No currency initialized"}
            active_jobs = conn.execute(
                "SELECT COUNT(*) FROM investigation_jobs WHERE world_id = ? AND status IN ('queued', 'processing')",
                (row["world_id"],),
            ).fetchone()[0]
            min_available = max(0, currency["max_balance"] - active_jobs)
            corrected = max(currency["current_balance"], min_available)
            if corrected != currency["current_balance"]:
                conn.execute(
                    "UPDATE world_currencies SET current_balance = ? WHERE world_id = ?",
                    (corrected, row["world_id"]),
                )
            return {
                "world_id": row["world_id"],
                "currency_type": currency["currency_type"],
                "balance": corrected,
                "max_balance": currency["max_balance"],
                "regen_rate": currency["regen_rate"],
            }

    def spend_investigation_points(
        self,
        amount: int,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Spend investigation points from a world's currency."""
        now = utc_now()
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            currency = conn.execute(
                "SELECT * FROM world_currencies WHERE world_id = ?",
                (row["world_id"],),
            ).fetchone()
            if not currency:
                raise ValueError("World currency not initialized")
            if currency["current_balance"] < amount:
                raise ValueError(f"Insufficient investigation points: need {amount}, have {currency['current_balance']}")
            new_balance = currency["current_balance"] - amount
            conn.execute(
                "UPDATE world_currencies SET current_balance = ? WHERE world_id = ?",
                (new_balance, row["world_id"]),
            )
            return {
                "world_id": row["world_id"],
                "spent": amount,
                "balance_before": currency["current_balance"],
                "balance_after": new_balance,
            }

    def restore_investigation_points(
        self,
        amount: int,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Restore investigation points (refund when investigation is collected)."""
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            currency = conn.execute(
                "SELECT * FROM world_currencies WHERE world_id = ?",
                (row["world_id"],),
            ).fetchone()
            if not currency:
                raise ValueError("World currency not initialized")
            new_balance = min(currency["current_balance"] + amount, currency["max_balance"])
            conn.execute(
                "UPDATE world_currencies SET current_balance = ? WHERE world_id = ?",
                (new_balance, row["world_id"]),
            )
            return {
                "world_id": row["world_id"],
                "restored": amount,
                "balance_after": new_balance,
                "max_balance": currency["max_balance"],
            }

    # --- State Tracking ---

    def record_investigation(
        self,
        item_name: str,
        world: str | None = None,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Record that an item has been investigated in a world."""
        now = utc_now()
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            state_id = make_id("invstate")
            conn.execute(
                """
                INSERT INTO investigation_state
                (state_id, world_id, entity_id, item_name, status, created_at, investigated_at)
                VALUES (?, ?, ?, ?, 'investigated', ?, ?)
                """,
                (state_id, row["world_id"], entity_id, item_name.strip(), now, now),
            )
            return {
                "state_id": state_id,
                "world_id": row["world_id"],
                "item_name": item_name.strip(),
                "entity_id": entity_id,
                "status": "investigated",
                "investigated_at": now,
            }

    def get_investigation_state(self, world: str | None = None) -> dict[str, Any]:
        """Get all investigations for a world."""
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            investigations = conn.execute(
                "SELECT * FROM investigation_state WHERE world_id = ? ORDER BY created_at ASC",
                (row["world_id"],),
            ).fetchall()
            return {
                "world_id": row["world_id"],
                "investigations": [
                    {
                        "state_id": inv["state_id"],
                        "item_name": inv["item_name"],
                        "entity_id": inv["entity_id"],
                        "status": inv["status"],
                        "created_at": inv["created_at"],
                        "investigated_at": inv["investigated_at"],
                    }
                    for inv in investigations
                ],
            }

    # --- Job Queue ---

    def create_investigation_job(
        self,
        entity_name: str,
        entity_type: str,
        world: str | None = None,
    ) -> dict[str, Any]:
        """Create an async investigation job."""
        now = utc_now()
        job_id = make_id("job")
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            conn.execute(
                """
                INSERT INTO investigation_jobs
                (job_id, world_id, entity_name, entity_type, status, created_at)
                VALUES (?, ?, ?, ?, 'queued', ?)
                """,
                (job_id, row["world_id"], entity_name.strip(), entity_type.strip(), now),
            )
            return {
                "job_id": job_id,
                "world_id": row["world_id"],
                "entity_name": entity_name.strip(),
                "entity_type": entity_type.strip(),
                "status": "queued",
                "created_at": now,
            }

    def get_investigation_job(self, job_id: str) -> dict[str, Any]:
        """Get status and result of an investigation job."""
        with self.connect() as conn:
            job = conn.execute(
                "SELECT * FROM investigation_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            if not job:
                raise ValueError(f"Investigation job not found: {job_id}")

            result = None
            if job["result_json"]:
                result = loads(job["result_json"], {})

            return {
                "job_id": job["job_id"],
                "world_id": job["world_id"],
                "entity_name": job["entity_name"],
                "entity_type": job["entity_type"],
                "status": job["status"],
                "entity_id": job["entity_id"],
                "result": result,
                "created_at": job["created_at"],
                "completed_at": job["completed_at"],
            }

    def complete_investigation_job(
        self,
        job_id: str,
        entity_id: str,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        """Mark an investigation job as complete with results."""
        now = utc_now()
        with self.connect() as conn:
            job = conn.execute(
                "SELECT * FROM investigation_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            if not job:
                raise ValueError(f"Investigation job not found: {job_id}")

            conn.execute(
                """
                UPDATE investigation_jobs
                SET status = 'complete', entity_id = ?, result_json = ?, completed_at = ?
                WHERE job_id = ?
                """,
                (entity_id, dumps(result), now, job_id),
            )

        return self.get_investigation_job(job_id)

    def get_investigation_queue(self, world: str | None = None, limit: int = 10) -> dict[str, Any]:
        """Get queued investigations for a world."""
        with self.connect() as conn:
            row = self._resolve_world(conn, world) if world else self._require_active_world(conn)
            jobs = conn.execute(
                "SELECT * FROM investigation_jobs WHERE world_id = ? AND status IN ('queued', 'processing') ORDER BY created_at ASC LIMIT ?",
                (row["world_id"], limit),
            ).fetchall()
            return {
                "world_id": row["world_id"],
                "jobs": [
                    {
                        "job_id": job["job_id"],
                        "entity_name": job["entity_name"],
                        "entity_type": job["entity_type"],
                        "status": job["status"],
                        "created_at": job["created_at"],
                    }
                    for job in jobs
                ],
            }
