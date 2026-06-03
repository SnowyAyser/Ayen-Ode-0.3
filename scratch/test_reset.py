import sys
import os
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ayen_ode.config import load_settings
from ayen_ode.services import AyenOdeService
from ayen_ode.relinker import clear_pending_pregenerations, auto_pre_generate_new_investigations

def test_reset():
    print("Loading settings...")
    settings = load_settings()
    print(f"Database path: {settings.db_path}")
    
    # Initialize service
    service = AyenOdeService(db_path=str(settings.db_path))
    
    # Find a world to test with
    with service.connect() as conn:
        row = conn.execute("SELECT world_id, name FROM worlds ORDER BY updated_at DESC LIMIT 1").fetchone()
        if not row:
            print("No worlds found to test.")
            return
        world_id = row["world_id"]
        world_name = row["name"]
        print(f"Testing reset on World '{world_name}' (ID: {world_id})")

    # Perform reset
    print("Calling service.reset_world...")
    try:
        result = service.reset_world(world_id)
        print("Reset successful!")
        print(f"Reset returned keys: {list(result.keys())}")
        
        # Test relinker clean
        print("Calling clear_pending_pregenerations...")
        clear_pending_pregenerations(world_id)
        print("Cleared successfully.")
        
        # Check original opening scene text
        original_text = result.get("original_opening_scene", "")
        print(f"Original opening scene length: {len(original_text)}")
        
        # Simulate background pre-generation
        if original_text:
            print("Testing auto_pre_generate_new_investigations")
            class MockClient:
                pass
            mock_client = MockClient()
            print("Spawning pre-generation with mock client...")
            try:
                import ayen_ode.relinker
                original_pregen = ayen_ode.relinker.pre_generate_investigation_handler
                
                # Mock pre_generate_investigation_handler to do nothing
                def mock_handler(*args, **kwargs):
                    print("  [Mock] pre_generate_investigation_handler called.")
                    return True
                ayen_ode.relinker.pre_generate_investigation_handler = mock_handler
                
                print("Running auto_pre_generate_new_investigations...")
                auto_pre_generate_new_investigations(mock_client, service, world_id, original_text)
                print("auto_pre_generate_new_investigations ran successfully!")
                
                # Restore
                ayen_ode.relinker.pre_generate_investigation_handler = original_pregen
            except Exception as e:
                print(f"Error running pregeneration: {e}")
                
    except Exception as e:
        print(f"Error resetting world: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reset()
