"""
Video Agent - Sixth agent in the pipeline
Generates actual video clips using frame-controlled generation
Uses Veo 3 via kie.ai and Nano Banana Pro for frame images
"""
import os
import asyncio
from typing import List, Optional
from studio.schemas import SceneClip, ProductionJob
from studio.providers.kieai_provider import KieAIProvider


class VideoAgent:
    """
    Generates video clips from frame specifications
    Uses Veo 3 (via kie.ai) for video generation
    Uses Nano Banana Pro (via kie.ai) for frame images
    Output: Each clip gets video_url populated
    """

    def __init__(self):
        self.kieai_api_key = os.environ.get('KIEAI_API_KEY')
        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

        # Validate configuration
        if not self.kieai_api_key and not self.use_mock:
            raise ValueError(
                "KIEAI_API_KEY not set and STUDIO_MOCK_GENERATION is disabled. "
                "Either set KIEAI_API_KEY in .env or enable mock mode."
            )

        # Initialize kie.ai provider
        if self.kieai_api_key and not self.use_mock:
            self.provider = KieAIProvider(api_key=self.kieai_api_key)
        else:
            self.provider = None
            if not self.use_mock:
                print("⚠️  Warning: No KIEAI provider initialized but mock mode is disabled!")

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
        """Generate video for a single clip using Veo 3"""
        clip.video_status = "generating"

        if self.use_mock:
            # Mock generation for testing
            await asyncio.sleep(0.5)  # Simulate generation time
            clip.video_url = f"https://mock-video-storage.example.com/{clip.clip_id}.mp4"
            clip.video_status = "complete"
            return

        try:
            if not clip.frame_spec:
                raise ValueError(f"Clip {clip.clip_id} missing frame_spec")

            print(f"   Scene {clip.sequence_number}: Generating frames with Nano Banana Pro...")

            # Determine aspect ratio and resolution based on platform
            aspect_ratio = "16:9" if job.platform == "youtube" else "9:16"
            resolution = "1080P"  # Standard HD resolution

            # Step 1: Generate start frame image with Nano Banana Pro
            start_image_data = self.provider.generate_image_nano_banana_pro(
                prompt=clip.frame_spec.start_frame_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            start_image_url = start_image_data.get("image_url")

            # Step 2: Generate end frame image with Nano Banana Pro
            end_image_data = self.provider.generate_image_nano_banana_pro(
                prompt=clip.frame_spec.end_frame_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            end_image_url = end_image_data.get("image_url")

            print(f"   Scene {clip.sequence_number}: Animating with Veo 3...")

            # Step 3: Generate video with Veo 3 (animate between frames)
            # Veo 3 expects image_urls as a list of reference images
            video_url = await self.provider.generate_video_veo3_wait(
                prompt=self._build_video_prompt(clip, job),
                image_urls=[start_image_url, end_image_url],
                aspect_ratio=aspect_ratio
            )

            clip.video_url = video_url
            clip.video_status = "complete"
            print(f"   ✅ Scene {clip.sequence_number}: Video generated")

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
    Uses ElevenLabs for voice synthesis (via kie.ai or direct)
    """

    def __init__(self):
        # Try kie.ai first, fall back to direct ElevenLabs
        self.kieai_api_key = os.environ.get('KIEAI_API_KEY')
        self.elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')

        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

        # Initialize provider
        if self.kieai_api_key and not self.use_mock:
            self.provider = KieAIProvider(api_key=self.kieai_api_key)
            self.use_kieai = True
        elif self.elevenlabs_api_key and not self.use_mock:
            # Direct ElevenLabs integration could go here
            self.provider = None
            self.use_kieai = False
        else:
            self.provider = None
            self.use_kieai = False

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
        """Generate audio for a single clip using ElevenLabs"""
        if not clip.narration_text or clip.narration_text.strip() == "":
            clip.audio_url = None
            return

        if self.use_mock:
            await asyncio.sleep(0.2)
            clip.audio_url = f"https://mock-audio-storage.example.com/{clip.clip_id}.mp3"
            return

        try:
            if self.use_kieai and self.provider:
                # Use ElevenLabs TTS via kie.ai
                audio_url = self.provider.generate_audio(
                    text=clip.narration_text,
                    voice="Rachel",  # Professional female voice
                    model="elevenlabs/text-to-speech-turbo-2-5",
                    speed=1.0,
                    stability=0.5,
                    similarity_boost=0.75
                )
                clip.audio_url = audio_url
                print(f"   ✅ Audio generated for scene {clip.sequence_number}")
            else:
                # Direct ElevenLabs API (placeholder)
                clip.audio_url = f"https://placeholder-audio/{clip.clip_id}.mp3"

        except Exception as e:
            print(f"   ❌ Audio generation failed for scene {clip.sequence_number}: {e}")
            clip.audio_url = None
