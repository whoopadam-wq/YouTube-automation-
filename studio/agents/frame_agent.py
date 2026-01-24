"""
Frame Agent - Fifth agent in the pipeline
Creates start/end frame specifications for controlled video generation
"""
import os
import json
from typing import List
from anthropic import Anthropic
from studio.schemas import SceneClip, FrameSpec, ProductionJob


class FrameAgent:
    """
    Creates precise start and end frame prompts for video generation
    This controls motion between two specific frames
    Output: Each clip gets a FrameSpec with start_frame_prompt and end_frame_prompt
    """

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=api_key) if api_key else None
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_frame_specs(self, job: ProductionJob, clips: List[SceneClip]) -> List[SceneClip]:
        """
        Generate start/end frame specifications for each scene

        Args:
            job: ProductionJob
            clips: List of SceneClip objects with all previous agent data

        Returns:
            Updated clips with frame_spec populated
        """
        print(f"🎞️  Frame Agent: Generating frame specs for {len(clips)} scenes...")

        if not self.client:
            print(f"   ⚠️  Skipping frame specs (add ANTHROPIC_API_KEY)")
            return clips

        for i, clip in enumerate(clips):
            # Determine transition from previous scene
            transition_type = "cut" if i == 0 else self._determine_transition(clips[i-1], clip)

            # Build comprehensive prompt context
            character_context = ""
            if clip.characters:
                char_descs = [f"{c.name}: {c.visual_description}" for c in clip.characters]
                character_context = f"Characters in scene:\n" + "\n".join(char_descs)

            lighting_context = ""
            if clip.lighting:
                lighting_context = f"""
Lighting:
- Type: {clip.lighting.lighting_type}
- Direction: {clip.lighting.direction}
- Intensity: {clip.lighting.intensity}
- Color: {clip.lighting.color_temperature}
- Mood: {clip.lighting.mood}
"""

            composition_context = ""
            if clip.composition:
                composition_context = f"""
Camera:
- Shot: {clip.composition.shot_type}
- Angle: {clip.composition.camera_angle}
- Movement: {clip.composition.camera_movement}
- Framing: {clip.composition.framing_notes}
- Depth: {clip.composition.depth_of_field}
"""

            prompt = f"""You are a video generation specialist. Create precise start and end frame prompts for this scene.

SCENE CONTEXT:
Scene {clip.sequence_number} of {len(clips)}
Description: {clip.scene_description}
Emotional Beat: {clip.emotional_beat}
Duration: {clip.duration} seconds

{character_context}

{lighting_context}

{composition_context}

Visual Style: {job.visual_style}
Platform: {job.platform}

TASK:
Create two detailed image prompts:
1. START FRAME: The exact frame the video should begin with
2. END FRAME: The exact frame the video should end on

The video generator will animate the motion BETWEEN these two frames.

Motion Description: Describe how the scene should move from start to end.

Return JSON:
{{
  "start_frame_prompt": "Ultra-detailed prompt for the starting frame (include all characters, lighting, composition, environment)",
  "end_frame_prompt": "Ultra-detailed prompt for the ending frame (show where motion leads to)",
  "motion_description": "Precise description of the motion/action between start and end",
  "transition_type": "{transition_type}",
  "duration_seconds": {clip.duration}
}}

IMPORTANT:
- Start and end frames should be DIFFERENT (show motion/change)
- Include character consistency details
- Be cinematically specific
- Match the lighting and composition specs
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse frame spec
            frame_data = self._parse_frame_response(response.content[0].text)

            # Create FrameSpec
            clip.frame_spec = FrameSpec(
                start_frame_prompt=frame_data.get('start_frame_prompt', clip.scene_description),
                end_frame_prompt=frame_data.get('end_frame_prompt', clip.scene_description),
                motion_description=frame_data.get('motion_description', 'smooth motion'),
                transition_type=transition_type,
                duration_seconds=clip.duration
            )

        print(f"✅ Frame Agent: Generated frame specifications")
        return clips

    def _determine_transition(self, prev_clip: SceneClip, current_clip: SceneClip) -> str:
        """Determine transition type between scenes"""
        # Simple heuristic - could be made smarter
        if prev_clip.emotional_beat != current_clip.emotional_beat:
            return "fade"
        return "cut"

    def _parse_frame_response(self, text: str) -> dict:
        """Parse LLM response into frame data"""
        try:
            # Find JSON object in response
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                return json.loads(json_text)
        except Exception as e:
            print(f"⚠️  Failed to parse frame JSON: {e}")

        # Fallback defaults
        return {
            "start_frame_prompt": "cinematic scene",
            "end_frame_prompt": "cinematic scene continued",
            "motion_description": "smooth camera movement",
            "transition_type": "cut",
            "duration_seconds": 5.0
        }
