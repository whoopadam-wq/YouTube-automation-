"""
Script Agent - First agent in the pipeline
Generates structured script with scene breakdown
"""
import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic
from studio.schemas import SceneClip, ProductionJob


class ScriptAgent:
    """
    Generates detailed scripts with scene-by-scene breakdown
    Output: List of SceneClip objects with script_content, narration_text, scene_description
    """

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_script(self, job: ProductionJob) -> List[SceneClip]:
        """
        Generate a complete script with scene breakdown

        Args:
            job: ProductionJob with title, topic, duration_target, tone, visual_style

        Returns:
            List of SceneClip objects with script data populated
        """
        print(f"📝 Script Agent: Generating script for '{job.title}'...")

        # Build prompt based on platform
        platform_guidance = self._get_platform_guidance(job.platform, job.duration_target)

        prompt = f"""You are a professional video scriptwriter. Create a detailed script for a video with the following specifications:

Title: {job.title}
Topic: {job.topic}
Duration: {job.duration_target} seconds
Visual Style: {job.visual_style}
Tone: {job.tone}
Platform: {job.platform}

{platform_guidance}

Create a scene-by-scene breakdown. For each scene, provide:
1. Scene number and duration
2. Narration text (what will be spoken)
3. Visual description (what should be shown)
4. Emotional beat (the feeling/mood)

Return your response as a JSON array of scenes with this structure:
[
  {{
    "sequence_number": 1,
    "duration": 5.0,
    "narration_text": "Text to be spoken",
    "scene_description": "Detailed visual description",
    "emotional_beat": "The mood/feeling",
    "script_content": "Combined scene script"
  }},
  ...
]

Make sure the total duration adds up to approximately {job.duration_target} seconds.
Create {self._estimate_scene_count(job.duration_target)} scenes.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        script_text = response.content[0].text
        scenes_data = self._parse_script_response(script_text)

        # Convert to SceneClip objects
        clips = []
        for scene_data in scenes_data:
            clip = SceneClip(
                clip_id=f"{job.job_id}_scene_{scene_data['sequence_number']}",
                sequence_number=scene_data['sequence_number'],
                script_content=scene_data.get('script_content', ''),
                narration_text=scene_data['narration_text'],
                scene_description=scene_data['scene_description'],
                emotional_beat=scene_data['emotional_beat'],
                duration=scene_data['duration']
            )
            clips.append(clip)

        print(f"✅ Script Agent: Generated {len(clips)} scenes")
        return clips

    def _get_platform_guidance(self, platform: str, duration: float) -> str:
        """Platform-specific guidance"""
        if platform == "youtube" or duration > 60:
            return """
YouTube long-form guidance:
- Hook viewers in first 5 seconds
- Build narrative with clear story arc
- Include 2-3 key moments/beats
- Strong conclusion with CTA
"""
        elif platform == "tiktok":
            return """
TikTok guidance:
- IMMEDIATE hook (first 0.5 seconds)
- Fast-paced, punchy scenes
- Trend-aware language
- Unexpected twist or payoff
- 9:16 vertical format
"""
        elif platform == "instagram":
            return """
Instagram Reels guidance:
- Visual-first approach
- Aesthetic consistency
- Text overlays friendly
- Shareable moment
- 9:16 vertical format
"""
        else:
            return "Multi-platform: Balance between depth and engagement"

    def _estimate_scene_count(self, duration: float) -> int:
        """Estimate appropriate number of scenes"""
        if duration <= 15:
            return 3  # Shorts: 3 quick scenes
        elif duration <= 30:
            return 4-5
        elif duration <= 60:
            return 6-8
        else:
            return max(8, int(duration / 10))  # ~10 seconds per scene for long-form

    def _parse_script_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured scene data"""
        # Try to extract JSON array from response
        try:
            # Find JSON array in response
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                scenes = json.loads(json_text)
                return scenes
        except Exception as e:
            print(f"⚠️  Failed to parse JSON, using fallback: {e}")

        # Fallback: create single scene
        return [{
            "sequence_number": 1,
            "duration": 10.0,
            "narration_text": "Script generation in progress...",
            "scene_description": "Visual content will be generated",
            "emotional_beat": "engaging",
            "script_content": text[:500]
        }]
