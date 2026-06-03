import unittest
from unittest.mock import MagicMock, patch
from ayen_ode.narrative.user_action import process_user_action


class TestUserAction(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_service = MagicMock()
        self.mock_service.list_entities.return_value = {
            "entities": [
                {"name": "old man", "entity_id": "1"},
                {"name": "guard", "entity_id": "2"}
            ]
        }
        self.world_id = "test_world"
        self.history = [{"role": "user", "content": "Hello"}]

    @patch("ayen_ode.narrative.stages.utils.set_stage_progress")
    @patch("ayen_ode.narrative.stages.utils.clear_stage_progress")
    def test_process_user_action_movement_detected(self, mock_clear, mock_set):
        # Mocking the assistant message returned by client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text='{"player.move": true, "move.direction": "towards", "towards.subject": "old man", "move.distance_inches": 36}')]
        self.mock_client.messages.create.return_value = mock_response

        response, updated_history, _, _, _ = process_user_action(
            client=self.mock_client,
            service=self.mock_service,
            world_id=self.world_id,
            user_action="I walk 3 feet towards the old man",
            conversation_history=self.history
        )

        self.assertIn('"player.move": true', response)
        self.assertEqual(len(updated_history), len(self.history) + 1)
        self.assertEqual(updated_history[-1]["role"], "assistant")
        self.assertIn("36", updated_history[-1]["content"])

    @patch("ayen_ode.narrative.stages.utils.set_stage_progress")
    @patch("ayen_ode.narrative.stages.utils.clear_stage_progress")
    def test_process_user_action_no_movement_detected(self, mock_clear, mock_set):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text='no_movement_detected: I did not detect a movement action. Please describe how you would like to move.')]
        self.mock_client.messages.create.return_value = mock_response

        response, updated_history, _, _, _ = process_user_action(
            client=self.mock_client,
            service=self.mock_service,
            world_id=self.world_id,
            user_action="I look at the sky",
            conversation_history=self.history
        )

        self.assertEqual(response, "I did not detect a movement action. Please describe how you would like to move.")
        self.assertEqual(len(updated_history), len(self.history) + 1)
        self.assertEqual(updated_history[-1]["content"], "I did not detect a movement action. Please describe how you would like to move.")

    @patch("ayen_ode.narrative.stages.utils.set_stage_progress")
    @patch("ayen_ode.narrative.stages.utils.clear_stage_progress")
    def test_process_user_action_self_default_rules(self, mock_clear, mock_set):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text='{"player.move": true, "move.direction": "north", "towards.subject": "self", "move.distance_inches": 60}')]
        self.mock_client.messages.create.return_value = mock_response

        response, updated_history, _, _, _ = process_user_action(
            client=self.mock_client,
            service=self.mock_service,
            world_id=self.world_id,
            user_action="I move 5 feet north",
            conversation_history=self.history
        )

        self.mock_client.messages.create.assert_called_once()
        called_kwargs = self.mock_client.messages.create.call_args[1]
        system_prompt = called_kwargs["system"]
        self.assertIn("- self", system_prompt)
        self.assertIn('"towards.subject": "self"', response)

    @patch("ayen_ode.narrative.stages.utils.set_stage_progress")
    @patch("ayen_ode.narrative.stages.utils.clear_stage_progress")
    def test_process_user_action_identify_action(self, mock_clear, mock_set):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text='{"player.identify": true, "identify.target": "wooden chest"}')]
        self.mock_client.messages.create.return_value = mock_response

        response, updated_history, _, _, _ = process_user_action(
            client=self.mock_client,
            service=self.mock_service,
            world_id=self.world_id,
            user_action="I look at the wooden chest",
            conversation_history=self.history
        )

        self.assertIn('"player.identify": true', response)
        self.assertIn('"identify.target": "wooden chest"', response)
        self.assertEqual(len(updated_history), len(self.history) + 1)


if __name__ == "__main__":
    unittest.main()
