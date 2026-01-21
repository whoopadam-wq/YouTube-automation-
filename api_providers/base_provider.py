"""
Base Provider
Abstract base class for all API providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseProvider(ABC):
    """
    Abstract base class for API providers.
    All providers must implement these methods.
    """

    def __init__(self, api_key: str, config: Dict[str, Any]):
        """
        Initialize provider.

        Args:
            api_key: API key for the provider
            config: Configuration dictionary
        """
        self.api_key = api_key
        self.config = config

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1920,
        height: int = 1080,
        **kwargs
    ) -> str:
        """
        Generate image from prompt.

        Args:
            prompt: Image generation prompt
            negative_prompt: Negative prompt (what to avoid)
            width: Image width
            height: Image height
            **kwargs: Provider-specific parameters

        Returns:
            URL or path to generated image
        """
        pass

    @abstractmethod
    async def generate_video(
        self,
        image_url: Optional[str] = None,
        prompt: Optional[str] = None,
        duration: int = 4,
        fps: int = 30,
        **kwargs
    ) -> str:
        """
        Generate video from image or prompt.

        Args:
            image_url: Starting image URL (for image-to-video)
            prompt: Text prompt for video generation
            duration: Video duration in seconds
            fps: Frames per second
            **kwargs: Provider-specific parameters

        Returns:
            URL or path to generated video
        """
        pass

    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            **kwargs: Provider-specific parameters

        Returns:
            URL or path to audio file
        """
        pass

    def estimate_cost(
        self,
        operation: str,
        **params
    ) -> float:
        """
        Estimate cost for an operation.

        Args:
            operation: Operation type (text, image, video, speech)
            **params: Operation parameters

        Returns:
            Estimated cost in USD
        """
        # Default implementation - override in subclasses for accurate costs
        cost_map = {
            'text': 0.05,
            'image': 0.10,
            'video': 2.00,
            'speech': 0.15
        }
        return cost_map.get(operation, 0.0)

    def validate_config(self) -> bool:
        """Validate provider configuration."""
        return self.api_key is not None and len(self.api_key) > 0

    def __repr__(self):
        """String representation."""
        return f"<{self.__class__.__name__}>"
