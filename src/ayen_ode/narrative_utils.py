"""Helpers for parsing and sanitizing Claude's investigation responses."""

from __future__ import annotations

import json as _json
import re
from typing import Any

from .services.base import STAT_NAMES_BY_ENTITY_TYPE


def parse_investigation_response(response_text: str, entity_type: str) -> dict[str, Any]:
    """Extract entity details from a Claude investigation response.

    Looks for a JSON block delimited by triple backticks; falls back to
    scanning for the first JSON object if no code fence is found.
    """
    for fence_start in ["```json", "```"]:
        if fence_start in response_text:
            try:
                block = response_text.split(fence_start, 1)[1]
                block = block.split("```")[0].strip()
                data = _json.loads(block)
                return sanitize_entity_details(data, entity_type)
            except Exception:
                pass

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        try:
            data = _json.loads(match.group(0))
            return sanitize_entity_details(data, entity_type)
        except Exception:
            pass

    return {}


def sanitize_entity_details(data: dict[str, Any], entity_type: str) -> dict[str, Any]:
    """Ensure entity detail fields have the correct types and valid stat names."""
    valid_stat_names = STAT_NAMES_BY_ENTITY_TYPE.get(entity_type, set())
    raw_stats = data.get("stats", {})
    sanitized_stats: dict[str, int] = {}
    for k, v in raw_stats.items():
        if k in valid_stat_names:
            try:
                sanitized_stats[k] = max(0, min(100, int(v)))
            except (TypeError, ValueError):
                pass
    return {
        "summary": str(data.get("summary", ""))[:500],
        "tags": [str(t) for t in data.get("tags", []) if t][:10],
        "timeline_notes": [str(n) for n in data.get("timeline_notes", []) if n][:5],
        "stats": sanitized_stats,
    }
