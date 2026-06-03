import json
import logging
import threading
from typing import Any

logger = logging.getLogger("ayen_ode.narrative.stages.utils")

_progress_lock = threading.Lock()
_active_progress: dict[str, str] = {}

def set_stage_progress(key: str, stage_desc: str) -> None:
    with _progress_lock:
        _active_progress[key] = stage_desc

def get_stage_progress(key: str) -> str | None:
    with _progress_lock:
        return _active_progress.get(key)

def clear_stage_progress(key: str) -> None:
    with _progress_lock:
        _active_progress.pop(key, None)

def run_stage_with_retry(client: Any, prompt: str, default_val: dict[str, Any], max_retries: int = 2) -> dict[str, Any]:
    """Query Qwen via completions with a robust, evidence-grounded, self-healing retry loop."""
    if not client:
        return default_val
        
    from ...config import HAIKU_MODEL
    current_prompt = prompt
    last_error = ""
    
    for attempt in range(max_retries + 1):
        if attempt > 0:
            logger.warning(f"Self-healing retry attempt {attempt}/{max_retries} due to JSON parse error: {last_error}")
            current_prompt = (
                f"{prompt}\n\n"
                f"CRITICAL WARNING (JSON FORMAT CORRECTION REQUIRED):\n"
                f"Your previous attempt produced invalid JSON or violated the strict schema rules.\n"
                f"Validation / Parsing Error: {last_error}\n"
                f"Please fix this immediately, ensure every conclusion is fully grounded in the provided context, "
                f"and return ONLY a valid, parseable JSON block. Do NOT include markdown fences, comments, or extra text."
            )
            
        try:
            response = client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": current_prompt}],
            )
            text = "".join(b.text for b in response.content if b.type == "text").strip()
            
            cleaned = text
            if "```json" in cleaned:
                cleaned = cleaned.split("```json", 1)[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```", 1)[1].split("```")[0].strip()
            elif "{" in cleaned:
                cleaned = "{" + cleaned.split("{", 1)[1]
                if "}" in cleaned:
                    cleaned = cleaned.rsplit("}", 1)[0] + "}"
                    
            data = json.loads(cleaned)
            if not isinstance(data, dict):
                raise ValueError("Response must be a structured JSON dictionary.")
            return data
            
        except Exception as e:
            last_error = str(e)
            
    logger.error(f"Failed to parse valid JSON after self-healing. Falling back to neutral default.")
    return default_val
