# backend/src/ai.py

from anthropic import Anthropic
from anthropic.types import MessageParam
from config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)


class AI:
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> None:
        self.client: Anthropic = client
        self.model: str = model
        self.max_tokens: int = max_tokens
        self.system_prompt: str | None = system_prompt

    def ask(self, messages: list[MessageParam]) -> tuple[str, int]:
        kwargs = {  # type: ignore
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }

        if self.system_prompt:
            kwargs["system"] = self.system_prompt  # type: ignore

        try:
            response = self.client.messages.create(**kwargs)  # type: ignore
        except Exception:
            return "", 0

        total_tokens = 0
        if hasattr(response, "usage"):  # type: ignore
            total_tokens = response.usage.input_tokens + response.usage.output_tokens  # type: ignore

        first_block = response.content[0]  # type: ignore
        if first_block.type == "text":  # type: ignore
            return first_block.text, total_tokens  # type: ignore
        return str(first_block), total_tokens  # type: ignore
