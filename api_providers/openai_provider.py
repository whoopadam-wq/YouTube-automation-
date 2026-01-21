"""
OpenAI Provider
OpenAI API implementation for text, image, and speech generation.
"""

import openai
from typing import Optional
from .base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, config: dict):
        """Initialize OpenAI provider."""
        super().__init__(api_key, config)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.text_model = config.get('models', {}).get('openai', 'gpt-4-turbo-preview')
        self.image_model = "dall-e-3"
        self.speech_model = "tts-1"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using GPT."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.text_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        **kwargs
    ) -> str:
        """Generate image using DALL-E."""
        # DALL-E 3 only supports specific sizes
        size = "1792x1024"  # Closest to 1920x1080

        response = await self.client.images.generate(
            model=self.image_model,
            prompt=prompt,
            size=size,
            quality="hd",
            n=1
        )

        return response.data[0].url

    async def generate_video(self, **kwargs) -> str:
        """OpenAI doesn't support video generation."""
        raise NotImplementedError("OpenAI does not support video generation")

    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Synthesize speech using OpenAI TTS."""
        voice = voice_id or "alloy"

        response = await self.client.audio.speech.create(
            model=self.speech_model,
            voice=voice,
            input=text
        )

        # Save to temporary file and return path
        import tempfile
        import os

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(response.content)
        temp_file.close()

        return temp_file.name

    def estimate_cost(self, operation: str, **params) -> float:
        """Estimate cost for OpenAI operations."""
        if operation == 'text':
            input_tokens = params.get('input_tokens', 2000)
            output_tokens = params.get('output_tokens', 2000)

            # GPT-4 Turbo pricing (per 1M tokens)
            input_cost = (input_tokens / 1_000_000) * 10.00
            output_cost = (output_tokens / 1_000_000) * 30.00

            return input_cost + output_cost

        elif operation == 'image':
            # DALL-E 3 HD pricing
            return 0.080

        elif operation == 'speech':
            # TTS pricing per 1M characters
            chars = params.get('characters', 1000)
            return (chars / 1_000_000) * 15.00

        return 0.0
