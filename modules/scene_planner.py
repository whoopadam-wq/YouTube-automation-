"""
Scene Planner Module
Breaks script into detailed scenes with visual and technical specifications.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class ScenePlan:
    """Detailed plan for a single scene."""
    scene_id: str
    narration_text: str
    characters_in_scene: List[str]
    environment_description: str
    lighting_design: str
    camera_distance: str
    camera_motion: str
    start_frame_prompt: str
    end_frame_prompt: str
    duration_seconds: float
    overlay_fx: List[str] = None

    def __post_init__(self):
        if self.overlay_fx is None:
            self.overlay_fx = []


class ScenePlanner:
    """
    Plans detailed scenes from script.
    Ensures scenes have motion and avoid static slideshow feel.
    """

    def __init__(self, config_manager, cost_tracker):
        """Initialize scene planner."""
        self.config = config_manager
        self.cost_tracker = cost_tracker

    async def plan_scenes(
        self,
        script: Dict[str, Any],
        characters: List[Dict],
        channel_config: Dict[str, Any]
    ) -> List[ScenePlan]:
        """
        Create detailed scene plans from script.

        Args:
            script: Script object
            characters: List of character objects
            channel_config: Channel configuration

        Returns:
            List of detailed ScenePlan objects
        """
        scene_plans = []

        for scene_data in script.get('scenes', []):
            scene_plan = await self._plan_single_scene(
                scene_data,
                characters,
                channel_config
            )
            scene_plans.append(scene_plan)

        return scene_plans

    async def _plan_single_scene(
        self,
        scene_data: Dict,
        characters: List[Dict],
        channel_config: Dict[str, Any]
    ) -> ScenePlan:
        """Plan a single scene in detail."""
        from api_providers import AnthropicProvider

        provider_config = self.config.get_provider_config('script_generation')
        api_key = self.config.get_api_key('anthropic')
        provider = AnthropicProvider(api_key, provider_config)

        # Build prompt
        prompt = f"""You are a cinematographer planning a scene for a {channel_config['niche']} video.

Visual Style: {channel_config['visual_style']}
Pacing: {channel_config['pacing_style']}

Scene Details:
- Narration: "{scene_data['narration_text']}"
- Visual Description: {scene_data['visual_description']}
- Duration: {scene_data['duration_seconds']} seconds
- Emotional Beat: {scene_data['emotional_beat']}

Available Characters: {', '.join([c.get('name', c['character_id']) for c in characters])}

Create a detailed scene plan with:
1. Environment description
2. Lighting design
3. Camera distance (close-up, medium, wide)
4. Camera motion (static, slow-pan, zoom-in, zoom-out, tracking)
5. Start frame prompt (detailed image description)
6. End frame prompt (for motion - how the scene evolves)
7. Characters appearing in this scene
8. Optional overlay effects

Output as JSON:
{{
  "environment_description": "detailed environment",
  "lighting_design": "lighting setup",
  "camera_distance": "close-up|medium|wide",
  "camera_motion": "static|slow-pan|zoom-in|zoom-out|tracking",
  "start_frame_prompt": "detailed start frame description",
  "end_frame_prompt": "detailed end frame description showing motion",
  "characters_in_scene": ["character_id1", "character_id2"],
  "overlay_fx": ["text overlay", "color grade", "etc"]
}}

Ensure motion between start and end frames to avoid static feel.
"""

        response = await provider.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1024
        )

        # Parse response
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()

            plan_data = json.loads(response)

            scene_plan = ScenePlan(
                scene_id=scene_data['scene_id'],
                narration_text=scene_data['narration_text'],
                characters_in_scene=plan_data.get('characters_in_scene', []),
                environment_description=plan_data.get('environment_description', ''),
                lighting_design=plan_data.get('lighting_design', 'natural'),
                camera_distance=plan_data.get('camera_distance', 'medium'),
                camera_motion=plan_data.get('camera_motion', 'static'),
                start_frame_prompt=plan_data.get('start_frame_prompt', ''),
                end_frame_prompt=plan_data.get('end_frame_prompt', ''),
                duration_seconds=scene_data['duration_seconds'],
                overlay_fx=plan_data.get('overlay_fx', [])
            )

            return scene_plan

        except Exception as e:
            print(f"Error planning scene: {e}")
            return self._create_fallback_scene_plan(scene_data, characters)

    def _create_fallback_scene_plan(
        self,
        scene_data: Dict,
        characters: List[Dict]
    ) -> ScenePlan:
        """Create fallback scene plan if LLM fails."""
        return ScenePlan(
            scene_id=scene_data['scene_id'],
            narration_text=scene_data['narration_text'],
            characters_in_scene=[],
            environment_description=scene_data.get('visual_description', ''),
            lighting_design='natural',
            camera_distance='medium',
            camera_motion='slow-pan',
            start_frame_prompt=scene_data.get('visual_description', ''),
            end_frame_prompt=scene_data.get('visual_description', '') + ", camera slowly pans across scene",
            duration_seconds=scene_data['duration_seconds'],
            overlay_fx=[]
        )

    def save_scene_plans(self, scene_plans: List[ScenePlan], output_path: str):
        """Save scene plans to file."""
        data = [asdict(plan) for plan in scene_plans]
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_scene_plans(self, input_path: str) -> List[ScenePlan]:
        """Load scene plans from file."""
        with open(input_path, 'r') as f:
            data = json.load(f)

        return [ScenePlan(**plan_data) for plan_data in data]
