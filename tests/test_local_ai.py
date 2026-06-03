from unittest.mock import patch, MagicMock
import unittest
import json

from ayen_ode.local_ai import LocalAIClient, MockTextBlock, MockToolUseBlock


class LocalAIIntegrationTests(unittest.TestCase):
    def test_local_ai_client_interface(self) -> None:
        client = LocalAIClient()
        self.assertIsNotNone(client.messages)

    @patch("urllib.request.urlopen")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-testkey"})
    def test_openrouter_routing(self, mock_urlopen) -> None:
        client = LocalAIClient()
        
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "OpenRouter test response."
                    }
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Test Gemini 2.5 Pro routing (for SONNET_MODEL)
        response = client.messages.create(
            model="google/gemini-2.5-pro",
            max_tokens=256,
            messages=[{"role": "user", "content": "Narrate something"}]
        )
        
        self.assertEqual(response.content[0].text, "OpenRouter test response.")
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        self.assertEqual(req.full_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(req.headers.get("Authorization"), "Bearer sk-or-testkey")
        
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "google/gemini-2.5-pro")
        
        # Test DeepSeek routing (for HAIKU_MODEL)
        response = client.messages.create(
            model="deepseek/deepseek-chat",
            max_tokens=256,
            messages=[{"role": "user", "content": "Extract something"}]
        )
        
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        payload = json.loads(req.data.decode("utf-8"))
        self.assertEqual(payload["model"], "deepseek/deepseek-chat")

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": ""})
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""})
    def test_openrouter_unconfigured_error(self) -> None:
        client = LocalAIClient()
        with self.assertRaises(ValueError):
            client.messages.create(
                model="google/gemini-2.5-pro",
                max_tokens=256,
                messages=[{"role": "user", "content": "Hello"}]
            )

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-or-testkey"})
    def test_qwen_disabled_error(self) -> None:
        client = LocalAIClient()
        with self.assertRaises(ValueError):
            client.messages.create(
                model="qwen2.5:14b",
                max_tokens=256,
                messages=[{"role": "user", "content": "Hello"}]
            )


if __name__ == "__main__":
    unittest.main()
