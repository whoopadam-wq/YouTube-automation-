"""
Anchor Character Manager
Manages persistent channel narrator character for intros/transitions/outros.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class AnchorCharacterManager:
    """
    Manages the persistent channel anchor/narrator character.
    Created once per channel, reused forever.
    """

    def __init__(self, config_manager, cost_tracker):
        """Initialize anchor character manager."""
        self.config = config_manager
        self.cost_tracker = cost_tracker
        self.cache_dir = config_manager.data_path / "channels"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_or_create_anchor(
        self,
        channel_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing anchor character or create new one.

        Args:
            channel_config: Channel configuration

        Returns:
            Anchor character data with reference image
        """
        if not channel_config.get('use_channel_character', False):
            return None

        channel_id = channel_config['channel_id']
        cache_file = self.cache_dir / f"{channel_id}_anchor.json"

        # Check cache
        if cache_file.exists():
            return self._load_anchor_from_cache(cache_file)

        # Create new anchor character
        anchor = await self._create_anchor_character(channel_config)

        # Save to cache
        self._save_anchor_to_cache(anchor, cache_file)

        return anchor

    async def _create_anchor_character(
        self,
        channel_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create anchor character with reference image."""
        from api_providers import ReplicateProvider, OpenAIProvider

        char_config = channel_config.get('channel_character', {})

        # Generate reference image
        provider_config = self.config.get_provider_config('image_generation')
        provider_name = provider_config.get('primary', 'replicate')
        api_key = self.config.get_api_key(provider_name)

        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
        else:
            provider = OpenAIProvider(api_key, provider_config)

        # Build prompt
        prompt = self._build_anchor_image_prompt(char_config, channel_config)

        # Generate image
        image_url = await provider.generate_image(
            prompt=prompt,
            width=1024,
            height=1024
        )

        anchor = {
            'name': char_config['name'],
            'visual_description': char_config['visual_description'],
            'personality': char_config['personality'],
            'voice_style': char_config['voice_style'],
            'appearance_frequency': char_config.get('appearance_frequency', 'intro_outro'),
            'reference_image_url': image_url,
            'channel_id': channel_config['channel_id']
        }

        # Track cost
        self.cost_tracker.record_cost(
            channel_id=channel_config['channel_id'],
            category='character_generation',
            provider=provider_name,
            amount=0.50
        )

        return anchor

    def _build_anchor_image_prompt(
        self,
        char_config: Dict,
        channel_config: Dict
    ) -> str:
        """Build prompt for anchor character image."""
        style = channel_config['visual_style']

        prompt = f"""Professional portrait: {char_config['visual_description']}.

Channel narrator for {channel_config['niche']} content.
Personality: {char_config['personality']}.
Visual style: {style}.

High quality, professional, engaging expression, perfect lighting.
Suitable for video thumbnail and presenter shots.
"""
        return prompt.strip()

    def _save_anchor_to_cache(self, anchor: Dict, cache_file: Path):
        """Save anchor to cache file."""
        with open(cache_file, 'w') as f:
            json.dump(anchor, f, indent=2)

    def _load_anchor_from_cache(self, cache_file: Path) -> Dict:
        """Load anchor from cache file."""
        with open(cache_file, 'r') as f:
            return json.load(f)

    async def generate_anchor_video_clip(
        self,
        anchor: Dict,
        clip_type: str,
        duration: float = 5.0
    ) -> str:
        """
        Generate a video clip of the anchor character.

        Args:
            anchor: Anchor character data
            clip_type: 'intro', 'transition', or 'outro'
            duration: Clip duration in seconds

        Returns:
            URL to generated video clip
        """
        # This would use audio-to-video generation (future: Runway, HeyGen, D-ID)
        # For now, return placeholder
        # TODO: Implement with actual audio-to-video API

        return anchor['reference_image_url']  # Placeholder

    def regenerate_anchor(self, channel_id: str):
        """Force regeneration of anchor character."""
        cache_file = self.cache_dir / f"{channel_id}_anchor.json"
        if cache_file.exists():
            cache_file.unlink()
