"""
Anthropic Provider
Claude API implementation for text generation.
"""

import anthropic
from typing import Optional
from .base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, config: dict):
        """Initialize Anthropic provider."""
        super().__init__(api_key, config)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config.get('models', {}).get('anthropic', 'claude-sonnet-4-5')

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Claude."""
        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }

        if system_prompt:
            params["system"] = system_prompt

        response = self.client.messages.create(**params)
        return response.content[0].text

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Anthropic doesn't support image generation."""
        raise NotImplementedError("Anthropic does not support image generation")

    async def generate_video(self, **kwargs) -> str:
        """Anthropic doesn't support video generation."""
        raise NotImplementedError("Anthropic does not support video generation")

    async def synthesize_speech(self, text: str, **kwargs) -> str:
        """Anthropic doesn't support speech synthesis."""
        raise NotImplementedError("Anthropic does not support speech synthesis")

    def estimate_cost(self, operation: str, **params) -> float:
        """Estimate cost for Anthropic operations."""
        if operation == 'text':
            # Rough estimate: ~750 words = ~1000 tokens
            input_tokens = params.get('input_tokens', 2000)
            output_tokens = params.get('output_tokens', 2000)

            # Claude Sonnet pricing (per 1M tokens)
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00

            return input_cost + output_cost

        return 0.0
