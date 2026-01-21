"""
Script Generator Module
Generates narration-first scripts for long-form and short-form content.
"""

import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class ScriptScene:
    """Represents a single scene in the script."""
    scene_id: str
    narration_text: str
    duration_seconds: float
    emotional_beat: str
    pacing_marker: str
    visual_description: str


@dataclass
class Script:
    """Complete script structure."""
    video_id: str
    channel_id: str
    content_type: str
    title: str
    description: str
    total_duration: float
    scenes: List[ScriptScene]
    metadata: Dict[str, Any]

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self):
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)


class ScriptGenerator:
    """
    Generates scripts for video content.
    Uses LLM to create structured, narration-first scripts.
    """

    def __init__(self, config_manager, cost_tracker):
        """Initialize script generator."""
        self.config = config_manager
        self.cost_tracker = cost_tracker

    async def generate_long_form_script(
        self,
        channel_config: Dict[str, Any],
        video_id: str
    ) -> Script:
        """
        Generate long-form script (8-12 minutes).

        Args:
            channel_config: Channel configuration
            video_id: Unique video ID

        Returns:
            Generated Script object
        """
        # Get provider
        provider_config = self.config.get_provider_config('script_generation')
        provider_name = provider_config.get('primary', 'anthropic')

        from api_providers import AnthropicProvider, OpenAIProvider

        api_key = self.config.get_api_key(provider_name)
        if provider_name == 'anthropic':
            provider = AnthropicProvider(api_key, provider_config)
        else:
            provider = OpenAIProvider(api_key, provider_config)

        # Build prompt
        system_prompt = self._build_system_prompt(channel_config, 'long_form')
        user_prompt = self._build_user_prompt(channel_config, 'long_form')

        # Generate script
        response = await provider.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.8
        )

        # Parse response into structured script
        script = self._parse_script_response(
            response,
            video_id,
            channel_config['channel_id'],
            'long_form',
            channel_config['target_long_duration']
        )

        # Track cost
        self.cost_tracker.record_cost(
            channel_id=channel_config['channel_id'],
            category='text_generation',
            provider=provider_name,
            amount=provider.estimate_cost('text', input_tokens=1000, output_tokens=3000),
            video_id=video_id
        )

        return script

    async def generate_short_form_script(
        self,
        channel_config: Dict[str, Any],
        video_id: str,
        hook_style: str = "question"
    ) -> Script:
        """
        Generate short-form script (30-90 seconds).

        Args:
            channel_config: Channel configuration
            video_id: Unique video ID
            hook_style: Hook style (question, bold_claim, teaser, dramatic)

        Returns:
            Generated Script object
        """
        # Get provider
        provider_config = self.config.get_provider_config('script_generation')
        provider_name = provider_config.get('primary', 'anthropic')

        from api_providers import AnthropicProvider, OpenAIProvider

        api_key = self.config.get_api_key(provider_name)
        if provider_name == 'anthropic':
            provider = AnthropicProvider(api_key, provider_config)
        else:
            provider = OpenAIProvider(api_key, provider_config)

        # Build prompt
        system_prompt = self._build_system_prompt(channel_config, 'short_form')
        user_prompt = self._build_user_prompt(
            channel_config,
            'short_form',
            hook_style=hook_style
        )

        # Generate script
        response = await provider.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.9
        )

        # Parse response
        script = self._parse_script_response(
            response,
            video_id,
            channel_config['channel_id'],
            'short_form',
            target_duration=60
        )

        # Track cost
        self.cost_tracker.record_cost(
            channel_id=channel_config['channel_id'],
            category='text_generation',
            provider=provider_name,
            amount=provider.estimate_cost('text', input_tokens=500, output_tokens=1000),
            video_id=video_id
        )

        return script

    def _build_system_prompt(
        self,
        channel_config: Dict[str, Any],
        content_type: str
    ) -> str:
        """Build system prompt for script generation."""
        base = f"""You are an expert YouTube content scriptwriter specializing in {channel_config['niche']}.

Your scripts must be:
- Engaging and emotionally resonant
- Optimized for viewer retention
- Structured for visual storytelling
- Narration-first (the visuals support the narration)

Channel Style:
- Pacing: {channel_config['pacing_style']}
- Visual Style: {channel_config['visual_style']}
- Tone Modifiers: {', '.join(channel_config['tone_style_modifiers'])}
"""

        if content_type == 'long_form':
            base += f"""
Content Format: Long-form video ({channel_config['target_long_duration']} minutes)

Structure Requirements:
- Strong hook in first 10 seconds
- Clear narrative arc with rising tension
- 3-5 major story beats
- Smooth transitions between scenes
- Satisfying conclusion

Output Format: JSON with this exact structure:
{{
  "title": "Compelling video title",
  "description": "SEO-optimized description",
  "scenes": [
    {{
      "scene_id": "scene_1",
      "narration_text": "The exact words to be spoken",
      "duration_seconds": 15,
      "emotional_beat": "curiosity|tension|surprise|relief|triumph",
      "pacing_marker": "slow|medium|fast",
      "visual_description": "Detailed description of what viewers see"
    }}
  ]
}}
"""
        else:  # short_form
            base += """
Content Format: Short-form video (60 seconds)

Structure Requirements:
- POWERFUL hook in first 3 seconds
- Single focused message
- Fast pacing, high energy
- Clear payoff at end
- Must work without sound (but narration enhances)

Output Format: JSON (same structure as above, 3-5 scenes max)
"""

        return base

    def _build_user_prompt(
        self,
        channel_config: Dict[str, Any],
        content_type: str,
        hook_style: str = "dramatic"
    ) -> str:
        """Build user prompt for script generation."""
        base_prompt = channel_config['base_prompt']

        if content_type == 'long_form':
            prompt = f"""{base_prompt}

Create a {channel_config['target_long_duration']}-minute video script about {channel_config['topic']}.

Requirements:
- Break into scenes of 10-30 seconds each
- Each scene must have clear visual direction
- Narration should be conversational and engaging
- Include emotional beats to maintain interest
- Scene transitions should feel natural

Generate the complete script in JSON format.
"""
        else:
            prompt = f"""{base_prompt}

Create a 60-second SHORT-FORM video about {channel_config['topic']}.

Hook Style: {hook_style}

Requirements:
- GRAB attention in first 3 seconds
- Deliver value quickly
- Build to a satisfying payoff
- Maximum 5 scenes
- Each scene 10-15 seconds

Generate the complete script in JSON format.
"""

        return prompt

    def _parse_script_response(
        self,
        response: str,
        video_id: str,
        channel_id: str,
        content_type: str,
        target_duration: float
    ) -> Script:
        """Parse LLM response into Script object."""
        try:
            # Try to extract JSON from response
            # LLMs sometimes wrap JSON in markdown code blocks
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()

            data = json.loads(response)

            # Parse scenes
            scenes = []
            for scene_data in data.get('scenes', []):
                scene = ScriptScene(
                    scene_id=scene_data.get('scene_id', f'scene_{len(scenes)+1}'),
                    narration_text=scene_data.get('narration_text', ''),
                    duration_seconds=float(scene_data.get('duration_seconds', 15)),
                    emotional_beat=scene_data.get('emotional_beat', 'neutral'),
                    pacing_marker=scene_data.get('pacing_marker', 'medium'),
                    visual_description=scene_data.get('visual_description', '')
                )
                scenes.append(scene)

            # Calculate total duration
            total_duration = sum(scene.duration_seconds for scene in scenes)

            # Create script
            script = Script(
                video_id=video_id,
                channel_id=channel_id,
                content_type=content_type,
                title=data.get('title', 'Untitled'),
                description=data.get('description', ''),
                total_duration=total_duration,
                scenes=scenes,
                metadata=data.get('metadata', {})
            )

            return script

        except Exception as e:
            # Fallback: create a simple script
            print(f"Error parsing script response: {e}")
            return self._create_fallback_script(
                video_id,
                channel_id,
                content_type,
                target_duration
            )

    def _create_fallback_script(
        self,
        video_id: str,
        channel_id: str,
        content_type: str,
        target_duration: float
    ) -> Script:
        """Create a fallback script if parsing fails."""
        num_scenes = 3 if content_type == 'short_form' else 5

        scenes = [
            ScriptScene(
                scene_id=f'scene_{i+1}',
                narration_text=f'Scene {i+1} narration',
                duration_seconds=target_duration * 60 / num_scenes,
                emotional_beat='neutral',
                pacing_marker='medium',
                visual_description=f'Scene {i+1} visuals'
            )
            for i in range(num_scenes)
        ]

        return Script(
            video_id=video_id,
            channel_id=channel_id,
            content_type=content_type,
            title='Fallback Script',
            description='',
            total_duration=target_duration * 60,
            scenes=scenes,
            metadata={'fallback': True}
        )
