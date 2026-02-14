# backend/src/ai.py

from anthropic import Anthropic
from anthropic.types import MessageParam
from config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)


class AI:
    def __init__(
        self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024
    ) -> None:
        self.client: Anthropic = client
        self.model: str = model
        self.max_tokens: int = max_tokens

    def ask(self, messages: list[MessageParam]) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
        )

        first_block = response.content[0]
        if first_block.type == "text":
            return first_block.text

        # fallback, quite ugly though
        return str(first_block)
