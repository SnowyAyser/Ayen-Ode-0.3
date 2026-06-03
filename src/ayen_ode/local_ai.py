"""AI Integration using OpenRouter (DeepSeek V3 and Gemini 2.5 Pro)."""

from __future__ import annotations
import json
import logging
import os
import urllib.request
from typing import Any

logger = logging.getLogger("ayen_ode.local_ai")

def get_local_ai_status() -> dict[str, Any]:
    # Ollama is removed entirely, always report ready to the client
    return {
        "ollama_running": True,
        "model_installed": True,
        "downloading": False,
        "download_progress": 1.0,
        "download_status": "Success",
    }

class MockTextBlock:
    def __init__(self, text: str):
        self.type, self.text = "text", text

class MockToolUseBlock:
    def __init__(self, name: str, tool_input: dict, id_: str):
        self.type, self.name, self.input, self.id = "tool_use", name, tool_input, id_

class MockResponse:
    def __init__(self, content: list):
        self.content = content

class MessagesAdapter:
    def create(
        self,
        model: str,
        max_tokens: int = 1024,
        system: str | None = None,
        messages: list[dict] = None,
        tools: list[dict] = None,
        tool_choice: dict = None,
    ) -> MockResponse:
        if messages is None:
            messages = []
        
        # Check if we should use OpenRouter
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not openrouter_key:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
            if anthropic_key.startswith("sk-or-"):
                openrouter_key = anthropic_key
        
        if not openrouter_key or openrouter_key == "sk-or-...":
            raise ValueError(
                "OpenRouter API key is not configured. "
                "Please click Settings on the dashboard to save your OpenRouter key."
            )

        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = "".join(text_parts)
            openai_messages.append({"role": role, "content": content})
        
        active_model = model
        if active_model == "qwen2.5:14b":
            raise ValueError(
                "Local model qwen2.5:14b is disabled. "
                "Please configure an OpenRouter API key to run Gemini and DeepSeek models."
            )
            
        try:
            payload = {
                "model": active_model,
                "messages": openai_messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": "https://github.com/SnowyAyser/Ayen-Ode-0.3",
                    "X-Title": "Ayen-Ode"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                res_data = json.loads(response.read().decode("utf-8"))
            
            choices = res_data.get("choices", [])
            if not choices:
                return MockResponse([MockTextBlock("Error: OpenRouter returned empty response.")])
            
            content_text = choices[0].get("message", {}).get("content") or ""
            return MockResponse([MockTextBlock(content_text)])
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return MockResponse([MockTextBlock(f"Error calling OpenRouter ({active_model}): {e}")])

class LocalAIClient:
    def __init__(self, api_key: str = None):
        self.messages = MessagesAdapter()
