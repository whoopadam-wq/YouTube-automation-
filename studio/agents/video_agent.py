"""
Video Agent - Sixth agent in the pipeline
Generates actual video clips using frame-controlled generation
"""
import os
import asyncio
from typing import List, Optional
from studio.schemas import SceneClip, ProductionJob


class VideoAgent:
    """
    Generates video clips from frame specifications
    Uses Replicate's video models (Stable Video Diffusion, etc.)
    Output: Each clip gets video_url populated
    """

    def __init__(self):
        self.api_token = os.environ.get('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not set")

        # For now, we'll use a placeholder - real implementation would use Replicate
        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

    async def generate_videos(self, job: ProductionJob, clips: List[SceneClip]) -> List[SceneClip]:
        """
        Generate video for each scene clip

        Args:
            job: ProductionJob
            clips: List of SceneClip objects with frame_spec

        Returns:
            Updated clips with video_url and video_status
        """
        print(f"🎥 Video Agent: Generating videos for {len(clips)} scenes...")

        # Generate videos in parallel (with concurrency limit)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent generations

        async def generate_clip_video(clip: SceneClip):
            async with semaphore:
                await self._generate_single_video(clip, job)

        # Run all generations in parallel
        await asyncio.gather(*[generate_clip_video(clip) for clip in clips])

        completed = sum(1 for c in clips if c.video_status == "complete")
        print(f"✅ Video Agent: Completed {completed}/{len(clips)} videos")

        return clips

    async def _generate_single_video(self, clip: SceneClip, job: ProductionJob):
        """Generate video for a single clip"""
        clip.video_status = "generating"

        if self.use_mock:
            # Mock generation for testing
            await asyncio.sleep(0.5)  # Simulate generation time
            clip.video_url = f"https://mock-video-storage.example.com/{clip.clip_id}.mp4"
            clip.video_status = "complete"
            return

        try:
            # Real implementation would use Replicate API
            # This is a placeholder for the actual integration

            if not clip.frame_spec:
                raise ValueError(f"Clip {clip.clip_id} missing frame_spec")

            # Build video generation prompt
            video_prompt = self._build_video_prompt(clip, job)

            # TODO: Actual Replicate API call
            # For now, mark as pending
            print(f"   Scene {clip.sequence_number}: Would generate with prompt: {video_prompt[:100]}...")

            # Placeholder: In real implementation, this would:
            # 1. Generate start frame image from start_frame_prompt
            # 2. Generate end frame image from end_frame_prompt
            # 3. Use video model to animate between frames
            # 4. Upload to storage
            # 5. Set video_url

            clip.video_url = f"https://placeholder-video/{clip.clip_id}.mp4"
            clip.video_status = "complete"

        except Exception as e:
            print(f"   ❌ Scene {clip.sequence_number} failed: {e}")
            clip.video_status = "failed"
            clip.video_url = None

    def _build_video_prompt(self, clip: SceneClip, job: ProductionJob) -> str:
        """Build comprehensive video generation prompt"""
        if not clip.frame_spec:
            return clip.scene_description

        prompt_parts = [
            f"START FRAME: {clip.frame_spec.start_frame_prompt}",
            f"END FRAME: {clip.frame_spec.end_frame_prompt}",
            f"MOTION: {clip.frame_spec.motion_description}",
            f"Duration: {clip.frame_spec.duration_seconds}s",
            f"Style: {job.visual_style}",
        ]

        if clip.lighting:
            prompt_parts.append(f"Lighting: {clip.lighting.lighting_type}, {clip.lighting.mood}")

        if clip.composition:
            prompt_parts.append(f"Camera: {clip.composition.shot_type}, {clip.composition.camera_movement}")

        return " | ".join(prompt_parts)


class AudioAgent:
    """
    Generates narration audio for scenes
    Uses ElevenLabs for voice synthesis
    """

    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")

        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

    async def generate_audio(self, job: ProductionJob, clips: List[SceneClip]) -> List[SceneClip]:
        """
        Generate narration audio for each scene

        Args:
            job: ProductionJob
            clips: List of SceneClip objects

        Returns:
            Updated clips with audio_url populated
        """
        print(f"🎙️  Audio Agent: Generating narration for {len(clips)} scenes...")

        for clip in clips:
            await self._generate_single_audio(clip)

        completed = sum(1 for c in clips if c.audio_url)
        print(f"✅ Audio Agent: Completed {completed}/{len(clips)} narrations")

        return clips

    async def _generate_single_audio(self, clip: SceneClip):
        """Generate audio for a single clip"""
        if not clip.narration_text or clip.narration_text.strip() == "":
            clip.audio_url = None
            return

        if self.use_mock:
            await asyncio.sleep(0.2)
            clip.audio_url = f"https://mock-audio-storage.example.com/{clip.clip_id}.mp3"
            return

        try:
            # TODO: Actual ElevenLabs API call
            # For now, placeholder
            clip.audio_url = f"https://placeholder-audio/{clip.clip_id}.mp3"

        except Exception as e:
            print(f"   ❌ Audio generation failed for scene {clip.sequence_number}: {e}")
            clip.audio_url = None
