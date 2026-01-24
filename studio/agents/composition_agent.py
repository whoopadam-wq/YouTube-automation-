"""
Composition Agent - Fourth agent in the pipeline
Plans camera angles, framing, and composition for each scene
"""
import os
import json
from typing import List
from anthropic import Anthropic
from studio.schemas import SceneClip, CompositionSpec, ProductionJob


class CompositionAgent:
    """
    Designs camera composition and framing for each scene
    Output: Each clip gets a CompositionSpec
    """

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=api_key) if api_key else None
        self.model = "claude-sonnet-4-5"

    async def design_composition(self, job: ProductionJob, clips: List[SceneClip]) -> List[SceneClip]:
        """
        Design camera composition for each scene

        Args:
            job: ProductionJob
            clips: List of SceneClip objects with script, characters, lighting

        Returns:
            Updated clips with composition populated
        """
        print(f"🎬 Composition Agent: Designing composition for {len(clips)} scenes...")

        if not self.client:
            print(f"   ⚠️  Skipping composition design (add ANTHROPIC_API_KEY)")
            return clips

        for clip in clips:
            # Build scene context
            lighting_context = ""
            if clip.lighting:
                lighting_context = f"Lighting: {clip.lighting.lighting_type}, {clip.lighting.mood}"

            scene_context = f"""
Scene {clip.sequence_number}:
Description: {clip.scene_description}
Emotional Beat: {clip.emotional_beat}
{lighting_context}
Characters: {[c.name for c in clip.characters] if clip.characters else "None"}
"""

            prompt = f"""You are a cinematography composition expert. Design camera setup for this scene.

Video Style: {job.visual_style}
Platform: {job.platform}

{scene_context}

Specify composition that enhances storytelling and matches the visual style.

Return JSON:
{{
  "shot_type": "wide|medium|close-up|extreme-close-up",
  "camera_angle": "eye-level|high|low|birds-eye|worms-eye",
  "camera_movement": "static|pan|tilt|zoom|dolly|tracking",
  "framing_notes": "detailed framing instructions",
  "rule_of_thirds": true|false,
  "depth_of_field": "shallow|medium|deep"
}}
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse composition spec
            comp_data = self._parse_composition_response(response.content[0].text)

            # Create CompositionSpec
            clip.composition = CompositionSpec(
                shot_type=comp_data.get('shot_type', 'medium'),
                camera_angle=comp_data.get('camera_angle', 'eye-level'),
                camera_movement=comp_data.get('camera_movement', 'static'),
                framing_notes=comp_data.get('framing_notes', ''),
                rule_of_thirds=comp_data.get('rule_of_thirds', True),
                depth_of_field=comp_data.get('depth_of_field', 'medium')
            )

        print(f"✅ Composition Agent: Completed composition design")
        return clips

    def _parse_composition_response(self, text: str) -> dict:
        """Parse LLM response into composition data"""
        try:
            # Find JSON object in response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
        except Exception as e:
            print(f"⚠️  Failed to parse composition JSON: {e}")

        # Fallback defaults
        return {
            "shot_type": "medium",
            "camera_angle": "eye-level",
            "camera_movement": "static",
            "framing_notes": "",
            "rule_of_thirds": True,
            "depth_of_field": "medium"
        }
