"""
Lighting Agent - Third agent in the pipeline
Plans lighting for each scene to match mood and style
"""
import os
import json
from typing import List
from anthropic import Anthropic
from studio.schemas import SceneClip, LightingSpec, ProductionJob


class LightingAgent:
    """
    Designs lighting specifications for each scene
    Output: Each clip gets a LightingSpec
    """

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=api_key) if api_key else None
        self.model = "claude-sonnet-4-5"

    async def design_lighting(self, job: ProductionJob, clips: List[SceneClip]) -> List[SceneClip]:
        """
        Design lighting for each scene

        Args:
            job: ProductionJob with visual_style and tone
            clips: List of SceneClip objects with script and characters

        Returns:
            Updated clips with lighting populated
        """
        print(f"💡 Lighting Agent: Designing lighting for {len(clips)} scenes...")

        if not self.client:
            print(f"   ⚠️  Skipping lighting design (add ANTHROPIC_API_KEY)")
            return clips

        for clip in clips:
            # Build scene context
            scene_context = f"""
Scene {clip.sequence_number}:
Description: {clip.scene_description}
Emotional Beat: {clip.emotional_beat}
Characters: {[c.name for c in clip.characters] if clip.characters else "None"}
"""

            prompt = f"""You are a cinematography lighting expert. Design lighting for this scene.

Video Style: {job.visual_style}
Tone: {job.tone}

{scene_context}

Specify lighting that enhances the mood and matches the visual style.

Return JSON:
{{
  "lighting_type": "natural|studio|dramatic|soft|hard",
  "direction": "front|back|side|top|bottom|mixed",
  "intensity": "low|medium|high",
  "color_temperature": "warm|neutral|cool",
  "mood": "describe the lighting mood",
  "technical_notes": "specific lighting setup details"
}}
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse lighting spec
            lighting_data = self._parse_lighting_response(response.content[0].text)

            # Create LightingSpec
            clip.lighting = LightingSpec(
                lighting_type=lighting_data.get('lighting_type', 'natural'),
                direction=lighting_data.get('direction', 'front'),
                intensity=lighting_data.get('intensity', 'medium'),
                color_temperature=lighting_data.get('color_temperature', 'neutral'),
                mood=lighting_data.get('mood', clip.emotional_beat),
                technical_notes=lighting_data.get('technical_notes', '')
            )

        print(f"✅ Lighting Agent: Completed lighting design")
        return clips

    def _parse_lighting_response(self, text: str) -> dict:
        """Parse LLM response into lighting data"""
        try:
            # Find JSON object in response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
        except Exception as e:
            print(f"⚠️  Failed to parse lighting JSON: {e}")

        # Fallback defaults
        return {
            "lighting_type": "natural",
            "direction": "front",
            "intensity": "medium",
            "color_temperature": "neutral",
            "mood": "balanced",
            "technical_notes": ""
        }
