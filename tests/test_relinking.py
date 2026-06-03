import json
import pytest
from pathlib import Path
from ayen_ode.relinker import run_database_relinking, relink_text_programmatically
from ayen_ode.service import AyenOdeService
from ayen_ode.config import Settings

def test_relink_text_programmatically():
    text = "The Skeleton rose from the grave and another Skeleton joined it."
    already_investigated = {"skeleton": "character"}
    
    relinked = relink_text_programmatically(text, already_investigated)
    # The programmatic relinker matches whole words case-insensitively and puts them in npc tags
    assert "<investigate npc='skeleton' cost='1'>Skeleton</investigate>" in relinked
    assert "<investigate npc='skeleton' cost='1'>skeleton</investigate>" in relinked.lower()

def test_run_database_relinking_offline(tmp_path):
    db_path = tmp_path / "test_ayen_ode.db"
    service = AyenOdeService(db_path)
    
    # 1. Initialize world
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO worlds (world_id, slug, name, status, premise, theme_tone, player_role, current_state_summary, active_tensions_json, last_system_handoff, created_at, updated_at) "
            "VALUES ('w1', 'w1-slug', 'Test World', 'active', 'Premise', 'Dark', 'Seeker', 'Summary', '[]', 'Handoff', '2026-01-01', '2026-01-01')"
        )
        # Add an investigated entity
        conn.execute(
            "INSERT INTO entities (entity_id, world_id, entity_type, name, summary, status, tags_json, timeline_notes_json, open_questions_json, metadata_json, created_at, updated_at) "
            "VALUES ('e1', 'w1', 'character', 'Skeleton', 'A dusty skeleton.', 'active', '[]', '[]', '[]', '{}', '2026-01-01', '2026-01-01')"
        )
        # Add an intake log that has references to the entity but is not yet linkified
        conn.execute(
            "INSERT INTO intake_logs (log_id, world_id, narrative_text, thought_process, tools_attempted_json, tools_executed_json, game_time_label, created_at) "
            "VALUES ('l1', 'w1', 'A Skeleton stood before us.', '{}', '[]', '[]', 'Day 1', '2026-01-01')"
        )
        conn.commit()
        
    # 2. Run the database relinking offline (API key = "" or "missing-api-key")
    class MockSettings:
        anthropic_api_key = "missing-api-key"
        anthropic_client = None
        
    run_database_relinking(service, MockSettings())
    
    # 3. Verify that the intake log was successfully relinked!
    with service.connect() as conn:
        log = conn.execute("SELECT narrative_text FROM intake_logs WHERE log_id = 'l1'").fetchone()
        assert log is not None
        assert "<investigate npc='skeleton' cost='1'>A Skeleton</investigate>" in log["narrative_text"]


def test_extract_heuristic_proper_nouns():
    from ayen_ode.relinker.parser import extract_heuristic_proper_nouns
    text = "The silver ship arrived at Citadel Vane. Meanwhile, Marcus Thell watched."
    nouns = extract_heuristic_proper_nouns(text)
    assert "Citadel Vane" in nouns
    assert "Marcus Thell" in nouns
    assert "The" not in nouns

    # Bullet points starting with capitalized verbs (should be skipped)
    bullet_text = "• Investigating the peaks revealed ancient ruins.\n- Exploring the valley showed secrets."
    bullet_nouns = extract_heuristic_proper_nouns(bullet_text)
    assert "Investigating" not in bullet_nouns
    assert "Exploring" not in bullet_nouns

    # Numbered items starting with capitalized verbs (should be skipped)
    numbered_text = "1. Searching the tower. 2) Opening the chest."
    numbered_nouns = extract_heuristic_proper_nouns(numbered_text)
    assert "Searching" not in numbered_nouns
    assert "Opening" not in numbered_nouns


def test_auto_pre_generate_new_investigations_heuristic(tmp_path):
    from ayen_ode.relinker.pregenerator import auto_pre_generate_new_investigations
    from ayen_ode.service import AyenOdeService
    import time
    
    db_path = tmp_path / "test_ayen_ode_heuristic.db"
    service = AyenOdeService(db_path)
    
    # Initialize world
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO worlds (world_id, slug, name, status, premise, theme_tone, player_role, current_state_summary, active_tensions_json, last_system_handoff, created_at, updated_at) "
            "VALUES ('w1', 'w1-slug', 'Test World', 'active', 'Premise', 'Dark', 'Seeker', 'Summary', '[]', 'Handoff', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
        
    class MockClient:
        def __init__(self):
            self.calls = []
        @property
        def messages(self):
            nonlocal mock_client
            class Messages:
                def create(self, **kwargs):
                    mock_client.calls.append(kwargs)
                    class Content:
                        def __init__(self):
                            self.text = "Mocked Narrative\n```json\n{\"summary\": \"A secret.\", \"tags\": [], \"timeline_notes\": [], \"stats\": {}}\n```"
                            self.type = "text"
                    class Response:
                        def __init__(self):
                            self.content = [Content()]
                    return Response()
            return Messages()
            
    mock_client = MockClient()
    text = "The silver ship arrived at Citadel Vane. Meanwhile, Marcus Thell watched."
    
    # We call auto_pre_generate_new_investigations. It should find "Citadel Vane" and "Marcus Thell".
    auto_pre_generate_new_investigations(mock_client, service, "w1", text)
    
    # Since it starts threads, wait up to 2 seconds for threads to execute
    start_time = time.time()
    while time.time() - start_time < 2.0:
        with service.connect() as conn:
            pregenned = conn.execute("SELECT entity_name FROM pregenerated_investigations WHERE world_id = 'w1'").fetchall()
            names = {row["entity_name"].lower() for row in pregenned}
            if "citadel vane" in names and "marcus thell" in names:
                break
        time.sleep(0.1)
        
    with service.connect() as conn:
        pregenned = conn.execute("SELECT entity_name FROM pregenerated_investigations WHERE world_id = 'w1'").fetchall()
        names = {row["entity_name"].lower() for row in pregenned}
        assert "citadel vane" in names
        assert "marcus thell" in names


def test_relink_world_history_logs(tmp_path):
    from ayen_ode.relinker.history_relinker import relink_world_history_logs
    from ayen_ode.service import AyenOdeService
    
    db_path = tmp_path / "test_ayen_ode_history.db"
    service = AyenOdeService(db_path)
    
    # 1. Initialize world
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO worlds (world_id, slug, name, status, premise, theme_tone, player_role, current_state_summary, active_tensions_json, last_system_handoff, created_at, updated_at) "
            "VALUES ('w1', 'w1-slug', 'Test World', 'active', 'Premise', 'Dark', 'Seeker', 'Summary', '[]', 'Handoff', '2026-01-01', '2026-01-01')"
        )
        # Add an investigated entity
        conn.execute(
            "INSERT INTO entities (entity_id, world_id, entity_type, name, summary, status, tags_json, timeline_notes_json, open_questions_json, metadata_json, created_at, updated_at) "
            "VALUES ('e1', 'w1', 'character', 'Vellmore', 'A politician.', 'active', '[]', '[]', '[]', '{}', '2026-01-01', '2026-01-01')"
        )
        # Add intake logs
        conn.execute(
            "INSERT INTO intake_logs (log_id, world_id, narrative_text, thought_process, tools_attempted_json, tools_executed_json, game_time_label, created_at) "
            "VALUES ('l1', 'w1', 'Vellmore was seen leaving the building.', '{}', '[]', '[]', 'Day 1', '2026-01-01')"
        )
        # Add world handoff
        conn.execute(
            "INSERT INTO world_handoffs (handoff_id, world_id, handoff_text, created_at) "
            "VALUES ('h1', 'w1', 'Report on Vellmore.', '2026-01-01')"
        )
        conn.commit()
        
    relink_world_history_logs(service, "w1")
    
    with service.connect() as conn:
        log = conn.execute("SELECT narrative_text FROM intake_logs WHERE log_id = 'l1'").fetchone()
        assert "<investigate npc='vellmore' cost='1'>Vellmore</investigate>" in log["narrative_text"]
        
        handoff = conn.execute("SELECT handoff_text FROM world_handoffs WHERE handoff_id = 'h1'").fetchone()
        assert "<investigate npc='vellmore' cost='1'>Vellmore</investigate>" in handoff["handoff_text"]


def test_exponential_backoff_retry(tmp_path, monkeypatch):
    import time
    from ayen_ode.relinker.pregenerator import auto_pre_generate_new_investigations
    from ayen_ode.service import AyenOdeService
    
    db_path = tmp_path / "test_ayen_ode_retry.db"
    service = AyenOdeService(db_path)
    
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO worlds (world_id, slug, name, status, premise, theme_tone, player_role, current_state_summary, active_tensions_json, last_system_handoff, created_at, updated_at) "
            "VALUES ('w1', 'w1-slug', 'Test World', 'active', 'Premise', 'Dark', 'Seeker', 'Summary', '[]', 'Handoff', '2026-01-01', '2026-01-01')"
        )
        conn.commit()

    attempts = 0
    original_get_handoff = service.get_world_handoff

    def mock_get_handoff(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts <= 2:
            raise Exception("Transient database error")
        return original_get_handoff(*args, **kwargs)

    monkeypatch.setattr(service, "get_world_handoff", mock_get_handoff)

    class MockMessages:
        def create(self, **kwargs):
            class Content:
                def __init__(self):
                    self.text = "Narrative text\n```json\n{\"summary\": \"Retry worked.\", \"tags\": [], \"timeline_notes\": [], \"stats\": {}}\n```"
                    self.type = "text"
            class Response:
                def __init__(self):
                    self.content = [Content()]
            return Response()

    class MockClient:
        @property
        def messages(self):
            return MockMessages()
            
    # Mock time.sleep to avoid waiting during test
    sleep_calls = []
    def mock_sleep(secs):
        sleep_calls.append(secs)
        
    monkeypatch.setattr(time, "sleep", mock_sleep)
    
    # We trigger auto_pre_generate_new_investigations for a new entity
    auto_pre_generate_new_investigations(MockClient(), service, "w1", "<investigate npc='Marcus' cost='1'>Marcus</investigate>")
    
    # Wait for the worker thread to finish
    start_time = time.time()
    while time.time() - start_time < 3.0:
        with service.connect() as conn:
            pregen = conn.execute("SELECT entity_name FROM pregenerated_investigations WHERE world_id = 'w1' AND entity_name = 'Marcus'").fetchone()
            if pregen:
                break
        time.sleep(0.01)
        
    with service.connect() as conn:
        pregen = conn.execute("SELECT entity_name FROM pregenerated_investigations WHERE world_id = 'w1' AND entity_name = 'Marcus'").fetchone()
        assert pregen is not None
        assert pregen["entity_name"] == "Marcus"
        
    assert attempts >= 3  # Initial attempt failed, 1st retry failed, 2nd retry succeeded
    assert 2.0 in sleep_calls
    assert 4.0 in sleep_calls


def test_get_all_linkable_entities(tmp_path):
    from ayen_ode.relinker import get_all_linkable_entities
    from ayen_ode.services.base import utc_now
    import json
    
    db_path = tmp_path / "test_linkable.db"
    service = AyenOdeService(db_path)
    
    # Create world row first to satisfy DB constraints
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO worlds (world_id, slug, name, status, premise, theme_tone, player_role, current_state_summary, active_tensions_json, last_system_handoff, created_at, updated_at) "
            "VALUES ('w_test_linkable', 'w-slug', 'Test World', 'active', 'Premise', 'Dark', 'Seeker', 'Summary', '[]', 'Handoff', '2026-01-01', '2026-01-01')"
        )
        conn.commit()
    
    # Insert one unlocked entity
    res = service.create_entity(
        name="Toll Warden",
        entity_type="character",
        summary="An unlocked toll warden.",
        world="w_test_linkable",
        tags=[],
        timeline_notes=[]
    )
    entity_id = res["entity"]["entity_id"]
    service.record_investigation("Toll Warden", "w_test_linkable", entity_id)
    
    # Insert one pregenerated investigation
    with service.connect() as conn:
        conn.execute(
            "INSERT INTO pregenerated_investigations (world_id, entity_name, entity_type, result_json, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            ("w_test_linkable", "Spoke Bridges", "location", json.dumps({"summary": "Pregenerated spoke bridge."}), utc_now())
        )
        
    linkables = get_all_linkable_entities(service, "w_test_linkable")
    
    # Assert both exist
    assert "Toll Warden" in linkables
    assert linkables["Toll Warden"] == "character"
    assert "Spoke Bridges" in linkables
    assert linkables["Spoke Bridges"] == "location"


def test_pregenerator_priority_queue(tmp_path):
    from ayen_ode.relinker.pregenerator import queue_pregeneration, _pregen_queue
    from ayen_ode.service import AyenOdeService
    
    db_path = tmp_path / "test_priority.db"
    service = AyenOdeService(db_path)
    
    class MockClient:
        pass
        
    # Clear any leftover queue state
    _pregen_queue.clear()
    
    # 1. Queue standard background task (priority=1)
    queue_pregeneration(MockClient(), service, "w1", "Toll Warden", "character", priority=1)
    assert len(_pregen_queue) == 1
    assert _pregen_queue[0]["name"] == "Toll Warden"
    assert _pregen_queue[0]["priority"] == 1
    
    # 2. Queue another background task (priority=1)
    queue_pregeneration(MockClient(), service, "w1", "Spoke Bridges", "location", priority=1)
    assert len(_pregen_queue) == 2
    assert _pregen_queue[1]["name"] == "Spoke Bridges"
    assert _pregen_queue[1]["priority"] == 1
    
    # 3. Queue high priority task (priority=0) -> should be sorted to the front!
    queue_pregeneration(MockClient(), service, "w1", "Caldera Deck", "location", priority=0)
    assert len(_pregen_queue) == 3
    assert _pregen_queue[0]["name"] == "Caldera Deck"  # Sorted to the front!
    assert _pregen_queue[0]["priority"] == 0
    
    # 4. Bump existing standard priority task "Spoke Bridges" to high priority (0)
    queue_pregeneration(MockClient(), service, "w1", "Spoke Bridges", "location", priority=0)
    # The queue length should stay 3 (not duplicate), and "Spoke Bridges" should be sorted in the front!
    assert len(_pregen_queue) == 3
    # First two should be priority 0
    assert _pregen_queue[0]["priority"] == 0
    assert _pregen_queue[1]["priority"] == 0
    assert {t["name"] for t in _pregen_queue[:2]} == {"Caldera Deck", "Spoke Bridges"}
    
    # Clear queue state
    _pregen_queue.clear()


def test_stop_words_elimination_protection():
    from ayen_ode.relinker import relink_text_programmatically
    
    # "Hope of Escape" is in already_investigated.
    already_investigated = {"Hope of Escape": "faction"}
    
    # A sentence with standard common words "hope" and "their"
    text = "Hope we find a way out soon. Their carriage was beautiful."
    relinked = relink_text_programmatically(text, already_investigated)
    
    # Standard words "hope" or "their" should NOT be linkified
    assert "<investigate" not in relinked
    
    # However, if the actual full canonical name is in the text, it SHOULD be linkified
    text_with_entity = "We are members of the Hope of Escape."
    relinked_with_entity = relink_text_programmatically(text_with_entity, already_investigated)
    assert "<investigate faction='hope of escape' cost='1'>the Hope of Escape</investigate>" in relinked_with_entity






