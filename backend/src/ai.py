# backend/src/ai.py

from anthropic import Anthropic
from anthropic.types import MessageParam
from config import ANTHROPIC_API_KEY
from typing import Any
import os

client = Anthropic(api_key=ANTHROPIC_API_KEY)
IS_DEV = os.getenv("FLASK_ENV") == "development"

def _log_token_count(client: Anthropic, model: str, messages: list[MessageParam]) -> None:
    try:
        count = client.messages.count_tokens(model=model, messages=messages)  # type: ignore
        print(f"✨ Input tokens: {count.input_tokens}")  # type: ignore
    except Exception as e:
        print(f"Could not count tokens: {e}")

def _log_usage(response: Any, model: str) -> None:
    print(f"✨ Usage: {response.usage}, model: {model}")  # type: ignore


class AI:
    def __init__(
        self, 
        model: str = "claude-sonnet-4-20250514", 
        max_tokens: int = 1024, 
        system_prompt: str | None = None
    ) -> None:
        self.client: Anthropic = client
        self.model: str = model
        self.max_tokens: int = max_tokens
        self.system_prompt: str | None = system_prompt

    def ask(self, messages: list[MessageParam]) -> str:
        if IS_DEV:
            _log_token_count(self.client, self.model, messages)

        kwargs = { # type: ignore
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        
        if self.system_prompt:
            kwargs["system"] = self.system_prompt  # type: ignore
        
        response = self.client.messages.create(**kwargs)  # type: ignore
        if IS_DEV:
            _log_usage(response, self.model) # type: ignore

        first_block = response.content[0]  # type: ignore
        if first_block.type == "text":  # type: ignore
            return first_block.text  # type: ignore

        return str(first_block) # type: ignore