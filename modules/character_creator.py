"""
Character Creator Module
Extracts characters from script and generates reference images.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Character:
    """Represents a character in the video."""
    character_id: str
    name: str
    role: str
    visual_description: str
    personality_traits: List[str]
    reference_image_url: str = None


class CharacterCreator:
    """
    Creates and manages characters from scripts.
    Ensures visual consistency across scenes.
    """

    def __init__(self, config_manager, cost_tracker):
        """Initialize character creator."""
        self.config = config_manager
        self.cost_tracker = cost_tracker

    async def extract_and_create_characters(
        self,
        script: Dict[str, Any],
        channel_config: Dict[str, Any]
    ) -> List[Character]:
        """
        Extract characters from script and generate reference images.

        Args:
            script: Script object
            channel_config: Channel configuration

        Returns:
            List of Character objects with reference images
        """
        # Step 1: Extract characters using LLM
        characters_data = await self._extract_characters(script, channel_config)

        # Step 2: Generate reference images for each character
        characters = []
        for char_data in characters_data:
            character = await self._generate_character_reference(
                char_data,
                channel_config
            )
            characters.append(character)

        return characters

    async def _extract_characters(
        self,
        script: Dict[str, Any],
        channel_config: Dict[str, Any]
    ) -> List[Dict]:
        """Extract character descriptions from script."""
        from api_providers import AnthropicProvider

        provider_config = self.config.get_provider_config('character_design')
        api_key = self.config.get_api_key('anthropic')
        provider = AnthropicProvider(api_key, provider_config)

        # Build scenes text
        scenes_text = "\n\n".join([
            f"Scene {i+1}: {scene['visual_description']}"
            for i, scene in enumerate(script.get('scenes', []))
        ])

        prompt = f"""Analyze this video script and extract all characters that need to be visualized.

Video Title: {script.get('title', '')}
Niche: {channel_config['niche']}
Visual Style: {channel_config['visual_style']}

Scenes:
{scenes_text}

For each character, provide:
1. Name (or descriptive identifier if unnamed)
2. Role in the story
3. Detailed visual description (appearance, clothing, setting)
4. Key personality traits

Output as JSON array:
[
  {{
    "character_id": "char_1",
    "name": "Character Name",
    "role": "protagonist/antagonist/narrator/etc",
    "visual_description": "Detailed visual description",
    "personality_traits": ["trait1", "trait2"]
  }}
]

Only include characters that appear visually. Limit to 3-5 main characters.
"""

        response = await provider.generate_text(
            prompt=prompt,
            temperature=0.6,
            max_tokens=2048
        )

        # Parse response
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()

            characters = json.loads(response)
            return characters if isinstance(characters, list) else []

        except Exception as e:
            print(f"Error parsing characters: {e}")
            return []

    async def _generate_character_reference(
        self,
        char_data: Dict,
        channel_config: Dict[str, Any]
    ) -> Character:
        """Generate reference image for a character."""
        from api_providers import ReplicateProvider, OpenAIProvider

        provider_config = self.config.get_provider_config('image_generation')
        provider_name = provider_config.get('primary', 'replicate')

        # Build image generation prompt
        prompt = self._build_character_image_prompt(char_data, channel_config)

        # Generate image
        api_key = self.config.get_api_key(provider_name)
        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
        else:
            provider = OpenAIProvider(api_key, provider_config)

        image_url = await provider.generate_image(
            prompt=prompt,
            width=1024,
            height=1024
        )

        # Create character object
        character = Character(
            character_id=char_data['character_id'],
            name=char_data['name'],
            role=char_data['role'],
            visual_description=char_data['visual_description'],
            personality_traits=char_data['personality_traits'],
            reference_image_url=image_url
        )

        # Track cost
        self.cost_tracker.record_cost(
            channel_id=channel_config['channel_id'],
            category='character_generation',
            provider=provider_name,
            amount=0.50
        )

        return character

    def _build_character_image_prompt(
        self,
        char_data: Dict,
        channel_config: Dict[str, Any]
    ) -> str:
        """Build optimized image generation prompt for character."""
        style = channel_config['visual_style']

        style_modifiers = {
            'gritty': 'dark, moody, film noir, high contrast',
            'clean': 'bright, minimalist, modern, clean lines',
            'dramatic': 'cinematic lighting, dramatic shadows, epic',
            'minimal': 'simple, clean background, focused',
            'vibrant': 'colorful, energetic, saturated colors'
        }

        prompt = f"""Professional character portrait: {char_data['visual_description']}.

Style: {style_modifiers.get(style, 'cinematic')}.
Mood: {', '.join(char_data['personality_traits'])}.

High quality, detailed, consistent lighting, professional photography.
"""

        return prompt.strip()

    def save_characters(
        self,
        characters: List[Character],
        output_path: str
    ):
        """Save character data to file."""
        data = [asdict(char) for char in characters]
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_characters(self, input_path: str) -> List[Character]:
        """Load characters from file."""
        with open(input_path, 'r') as f:
            data = json.load(f)

        return [Character(**char_data) for char_data in data]
