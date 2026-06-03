import logging
import threading
import concurrent.futures
import json
import time
from typing import Any
from .parser import extract_investigate_tags, get_name_variants

logger = logging.getLogger("ayen_ode.relinker.pregenerator")

_pregen_queue: list[dict[str, Any]] = []
_pregen_lock = threading.Lock()
_pregen_condition = threading.Condition(_pregen_lock)

_active_pregenerations: set[tuple[str, str]] = set()
_active_pregenerations_lock = threading.Lock()

_workers_started = False


def clear_pending_pregenerations(world_id: str) -> None:
    """Remove all pending pre-generation keys for a given world (e.g. after reset)."""
    with _pregen_lock:
        global _pregen_queue
        _pregen_queue = [t for t in _pregen_queue if t["world_id"] != world_id]


def queue_pregeneration(
    client: Any,
    service: Any,
    world_id: str,
    name: str,
    etype: str,
    priority: int,
    context: str = ""
) -> None:
    """Submit a task to the priority background pre-generation queue.
    
    Priority levels:
        0 = High (Interactive / User clicked or hovered)
        1 = Standard (Background relinker heuristic scan)
    
    If an item is already queued with standard priority (1), it gets dynamically
    bumped to high priority (0) and sorted to the front of the queue.
    """
    if not client or not name or not name.strip():
        return

    name_clean = name.strip()
    key = (world_id, name_clean.lower())

    global _workers_started
    with _pregen_lock:
        # Start worker pool on first call
        if not _workers_started:
            for i in range(3):
                t = threading.Thread(
                    target=_pregen_worker_loop,
                    name=f"BgPreGen-{i}",
                    daemon=True
                )
                t.start()
            _workers_started = True

        # Check if currently being processed in a worker thread
        with _active_pregenerations_lock:
            if key in _active_pregenerations:
                return

        # Check if already in the queue waiting
        existing_task = None
        for t in _pregen_queue:
            if (t["world_id"], t["name"].lower()) == key:
                existing_task = t
                break

        if existing_task:
            # Bump priority if the new request has higher priority
            if existing_task["priority"] > priority:
                existing_task["priority"] = priority
                if context:
                    existing_task["context"] = context
                existing_task["client"] = client
                existing_task["service"] = service
                _pregen_queue.sort(key=lambda x: (x["priority"], x["created_at"]))
                logger.info(f"Bumped existing pregeneration task '{name_clean}' to priority {priority}.")
            return

        # Add new task and re-sort queue
        task = {
            "priority": priority,
            "world_id": world_id,
            "name": name_clean,
            "etype": etype,
            "context": context,
            "client": client,
            "service": service,
            "created_at": time.monotonic()
        }
        _pregen_queue.append(task)
        _pregen_queue.sort(key=lambda x: (x["priority"], x["created_at"]))
        _pregen_condition.notify()
        logger.info(f"Queued pregeneration for '{name_clean}' (priority={priority}).")


def auto_pre_generate_new_investigations(client: Any, service: Any, world_id: str, text: str) -> None:
    """Scan text for investigate tags and heuristic proper nouns, and background-pregenerate any new entities."""
    if not client:
        return

    items = extract_investigate_tags(text) or []
    
    from .parser import extract_heuristic_proper_nouns
    proper_nouns = extract_heuristic_proper_nouns(text)
    
    explicit_names = {name.strip().lower() for name, _ in items}
    for noun in proper_nouns:
        if noun.strip().lower() not in explicit_names:
            items.append((noun, "object"))

    for name, etype in items:
        queue_pregeneration(client, service, world_id, name, etype, priority=1)


def _pregen_worker_loop() -> None:
    """Worker thread loop that polls the priority queue and processes tasks sequentially."""
    from ..narrative import investigate_entity
    from ..services.base import utc_now

    while True:
        task = None
        with _pregen_lock:
            while not _pregen_queue:
                _pregen_condition.wait()
            task = _pregen_queue.pop(0)

        if not task:
            continue

        world_id = task["world_id"]
        name = task["name"]
        etype = task["etype"]
        priority = task["priority"]
        context = task["context"]
        client = task["client"]
        service = task["service"]
        key = (world_id, name.lower())

        with _active_pregenerations_lock:
            _active_pregenerations.add(key)

        try:
            variants = get_name_variants(name)
            placeholders = ",".join("?" for _ in variants)

            # 1. Check if already unlocked (entities table)
            with service.connect() as conn:
                already_exists = conn.execute(
                    f"SELECT 1 FROM entities WHERE world_id = ? AND LOWER(name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_exists:
                    continue

                # 2. Check if already pre-generated in SQLite database
                already_pregenerated = conn.execute(
                    f"SELECT 1 FROM pregenerated_investigations WHERE world_id = ? AND LOWER(entity_name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_pregenerated:
                    continue

            logger.info(f"Processing pregeneration: '{name}' ({etype}), priority={priority}")
            
            max_retries = 3
            delay = 2.0
            for attempt in range(max_retries + 1):
                try:
                    result = investigate_entity(
                        client,
                        service,
                        world_id,
                        name,
                        etype,
                        [],
                        save_to_db=False,
                        context=context or "Discovered in previous narrative or compendium card."
                    )
                    now = utc_now()
                    with service.connect() as conn:
                        conn.execute(
                            "INSERT OR REPLACE INTO pregenerated_investigations"
                            " (world_id, entity_name, entity_type, result_json, created_at)"
                            " VALUES (?, ?, ?, ?, ?)",
                            (world_id, name.strip(), etype.strip(), json.dumps(result), now),
                        )
                    break  # Success!
                except Exception as e:
                    if attempt < max_retries:
                        logger.warning(f"Error pregenerating {name} (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= 2.0
                    else:
                        logger.error(f"Failed to pregenerate {name} after {max_retries + 1} attempts: {e}")
        except Exception as e:
            logger.error(f"Pregeneration task failed: {e}")
        finally:
            with _active_pregenerations_lock:
                _active_pregenerations.discard(key)


def pre_generate_scene_investigations_sync(client: Any, service: Any, world_id: str, text: str) -> None:
    """Extract tags and pre-generate all of them concurrently, waiting for completion."""
    if not client:
        return

    items = extract_investigate_tags(text)
    if not items:
        return

    from ..narrative import investigate_entity
    from ..services.base import utc_now

    def worker(name: str, etype: str):
        try:
            variants = get_name_variants(name)
            placeholders = ",".join("?" for _ in variants)

            with service.connect() as conn:
                already_exists = conn.execute(
                    f"SELECT 1 FROM entities WHERE world_id = ? AND LOWER(name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_exists:
                    return

                already_pregenerated = conn.execute(
                    f"SELECT 1 FROM pregenerated_investigations WHERE world_id = ? AND LOWER(entity_name) IN ({placeholders})",
                    [world_id] + variants
                ).fetchone()
                if already_pregenerated:
                    return

            logger.info(f"Synchronously pre-generating: {name} ({etype})")
            result = investigate_entity(
                client,
                service,
                world_id,
                name,
                etype,
                [],
                save_to_db=False,
                context="Pre-generated during world loading."
            )
            now = utc_now()
            with service.connect() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO pregenerated_investigations"
                    " (world_id, entity_name, entity_type, result_json, created_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (world_id, name.strip(), etype.strip(), json.dumps(result), now),
                )
        except Exception as e:
            logger.warning(f"Failed pre-generating {name}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, name, etype) for name, etype in items]
        concurrent.futures.wait(futures)
