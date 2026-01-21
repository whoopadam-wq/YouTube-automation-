"""
ElevenLabs Provider
ElevenLabs API implementation for voice synthesis.
"""

from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs
from typing import Optional
import tempfile
from .base_provider import BaseProvider


class ElevenLabsProvider(BaseProvider):
    """ElevenLabs API provider for voice synthesis."""

    def __init__(self, api_key: str, config: dict):
        """Initialize ElevenLabs provider."""
        super().__init__(api_key, config)
        self.client = ElevenLabs(api_key=api_key)
        self.model_id = config.get('settings', {}).get('model_id', 'eleven_turbo_v2')

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """ElevenLabs doesn't support text generation."""
        raise NotImplementedError("Use Anthropic or OpenAI for text generation")

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """ElevenLabs doesn't support image generation."""
        raise NotImplementedError("Use Replicate or OpenAI for image generation")

    async def generate_video(self, **kwargs) -> str:
        """ElevenLabs doesn't support video generation."""
        raise NotImplementedError("Use Replicate for video generation")

    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Synthesize speech using ElevenLabs."""
        # Default to a neutral voice if not specified
        voice = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

        # Voice settings
        stability = self.config.get('settings', {}).get('stability', 0.5)
        similarity_boost = self.config.get('settings', {}).get('similarity_boost', 0.75)

        # Generate audio
        audio = self.client.generate(
            text=text,
            voice=voice,
            model=self.model_id,
            voice_settings=VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost
            )
        )

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        save(audio, temp_file.name)

        return temp_file.name

    def estimate_cost(self, operation: str, **params) -> float:
        """Estimate cost for ElevenLabs operations."""
        if operation == 'speech':
            # ElevenLabs charges per character
            # Approximately $0.30 per 1000 characters
            chars = params.get('characters', len(params.get('text', '')))
            return (chars / 1000) * 0.30

        return 0.0

    def get_available_voices(self) -> list:
        """Get list of available voices."""
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category
                }
                for voice in voices.voices
            ]
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
