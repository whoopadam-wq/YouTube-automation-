"""
Shorts Generator Module
Derives short-form content from long-form videos or generates standalone shorts.
"""

from typing import Dict, List, Any
import asyncio


class ShortsGenerator:
    """
    Generates short-form content (30-90 seconds).
    Can derive from long-form or create standalone.
    """

    def __init__(
        self,
        config_manager,
        cost_tracker,
        script_generator,
        media_generator,
        video_assembler
    ):
        """Initialize shorts generator."""
        self.config = config_manager
        self.cost_tracker = cost_tracker
        self.script_generator = script_generator
        self.media_generator = media_generator
        self.video_assembler = video_assembler

    async def generate_shorts_from_long_form(
        self,
        long_form_script: Dict,
        long_form_media: List[Dict],
        channel_config: Dict,
        num_shorts: int = 3
    ) -> List[str]:
        """
        Derive shorts from long-form content.

        Args:
            long_form_script: Original long-form script
            long_form_media: Media assets from long-form
            channel_config: Channel configuration
            num_shorts: Number of shorts to create

        Returns:
            List of paths to generated shorts
        """
        shorts = []

        # Extract best moments from long-form
        moments = self._identify_best_moments(long_form_script, num_shorts)

        # Generate each short
        tasks = [
            self._create_short_from_moment(
                moment,
                long_form_media,
                channel_config,
                f"short_{i+1}"
            )
            for i, moment in enumerate(moments)
        ]

        shorts = await asyncio.gather(*tasks)
        return shorts

    async def generate_standalone_shorts(
        self,
        channel_config: Dict,
        num_shorts: int = 3
    ) -> List[str]:
        """
        Generate standalone shorts (not derived from long-form).

        Args:
            channel_config: Channel configuration
            num_shorts: Number of shorts to create

        Returns:
            List of paths to generated shorts
        """
        shorts = []

        hook_styles = ['question', 'bold_claim', 'teaser', 'dramatic']

        for i in range(num_shorts):
            video_id = f"short_{channel_config['channel_id']}_{i}"
            hook = hook_styles[i % len(hook_styles)]

            # Generate script
            script = await self.script_generator.generate_short_form_script(
                channel_config=channel_config,
                video_id=video_id,
                hook_style=hook
            )

            # Generate media (simplified scene planning for shorts)
            scene_plans = [
                {
                    'scene_id': scene['scene_id'],
                    'start_frame_prompt': scene['visual_description'],
                    'end_frame_prompt': scene['visual_description'],
                    'environment_description': 'dynamic',
                    'lighting_design': 'dramatic',
                    'camera_distance': 'close-up',
                    'duration_seconds': scene['duration_seconds']
                }
                for scene in script.scenes
            ]

            media = await self.media_generator.generate_scene_media(
                scene_plans,
                channel_config,
                video_id
            )

            # Generate narration
            narration_path = await self._generate_narration(
                script.scenes,
                channel_config
            )

            # Assemble
            short_path = await self.video_assembler.assemble_video(
                scene_media=media,
                narration_audio=narration_path,
                video_id=video_id,
                metadata={'title': script.title, 'description': script.description}
            )

            shorts.append(short_path)

        return shorts

    def _identify_best_moments(
        self,
        script: Dict,
        num_moments: int
    ) -> List[Dict]:
        """Identify best moments from long-form for shorts."""
        scenes = script.get('scenes', [])

        # Score scenes based on emotional impact
        scored_scenes = []
        for scene in scenes:
            score = self._score_scene_for_shorts(scene)
            scored_scenes.append((score, scene))

        # Sort by score and take top N
        scored_scenes.sort(reverse=True, key=lambda x: x[0])
        return [scene for _, scene in scored_scenes[:num_moments]]

    def _score_scene_for_shorts(self, scene: Dict) -> float:
        """Score a scene for shorts potential."""
        score = 0.0

        # High emotional beats score higher
        emotional_weights = {
            'curiosity': 0.8,
            'tension': 1.0,
            'surprise': 0.9,
            'triumph': 0.7,
            'shock': 1.0
        }

        beat = scene.get('emotional_beat', 'neutral')
        score += emotional_weights.get(beat, 0.5)

        # Fast pacing scores higher
        if scene.get('pacing_marker') == 'fast':
            score += 0.5

        # Short scenes are better for shorts
        duration = scene.get('duration_seconds', 15)
        if duration <= 20:
            score += 0.3

        return score

    async def _create_short_from_moment(
        self,
        moment: Dict,
        media_assets: List[Dict],
        channel_config: Dict,
        short_id: str
    ) -> str:
        """Create a short video from a moment."""
        # Find media for this scene
        scene_media = [
            asset for asset in media_assets
            if asset.get('scene_id') == moment.get('scene_id')
        ]

        if not scene_media:
            return None

        # Generate hook overlay
        hook_text = self._generate_hook_text(moment)

        # Assemble short
        short_path = await self.video_assembler.assemble_video(
            scene_media=scene_media,
            narration_audio=None,  # Use original audio
            video_id=short_id,
            metadata={'title': hook_text}
        )

        # Add hook overlay
        if hook_text:
            short_path = await self.video_assembler.add_text_overlay(
                video_path=short_path,
                text=hook_text,
                duration=3.0,
                position='top'
            )

        return short_path

    def _generate_hook_text(self, moment: Dict) -> str:
        """Generate hook text for a moment."""
        narration = moment.get('narration_text', '')

        # Extract first compelling sentence
        sentences = narration.split('.')
        if sentences:
            return sentences[0].strip()[:50]  # Max 50 chars

        return "Watch this!"

    async def _generate_narration(
        self,
        scenes: List,
        channel_config: Dict
    ) -> str:
        """Generate narration audio for scenes."""
        from api_providers import ElevenLabsProvider

        provider_config = self.config.get_provider_config('voice_synthesis')
        api_key = self.config.get_api_key('elevenlabs')
        provider = ElevenLabsProvider(api_key, provider_config)

        # Combine all narration
        full_text = " ".join([scene['narration_text'] for scene in scenes])

        # Synthesize
        audio_path = await provider.synthesize_speech(
            text=full_text,
            voice_id=None  # Use default
        )

        return audio_path

    async def optimize_for_platform(
        self,
        short_path: str,
        platform: str = "youtube_shorts"
    ) -> str:
        """Optimize short for specific platform (aspect ratio, duration, etc.)."""
        # YouTube Shorts: 9:16, max 60s
        # TikTok: 9:16, max 60s
        # Instagram Reels: 9:16, max 90s

        # For now, ensure 9:16 aspect ratio
        import subprocess

        output_path = short_path.replace('.mp4', '_optimized.mp4')

        cmd = [
            'ffmpeg',
            '-i', short_path,
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
