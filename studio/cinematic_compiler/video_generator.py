"""
Cinematic Video Generator
Integrates compiled prompts with Veo 3 and Nano Banana APIs
"""
import os
from typing import Optional, Dict, Any
from .schemas import CinematicProject, CinematicScene


class CinematicVideoGenerator:
    """
    Generates videos and images from compiled cinematic prompts

    Integrates with:
    - Veo 3 (via kie.ai) for video generation
    - Nano Banana Pro (via kie.ai) for frame image generation

    Uses deterministic prompts from CinematicCompiler
    """

    def __init__(self, kieai_api_key: Optional[str] = None):
        """
        Initialize video generator

        Args:
            kieai_api_key: kie.ai API key (defaults to env var)
        """
        self.api_key = kieai_api_key or os.environ.get('KIEAI_API_KEY')

        if not self.api_key:
            print("⚠️  Warning: KIEAI_API_KEY not set. Video generation will be disabled.")

    def generate_frame_images(
        self,
        scene: CinematicScene,
        project: CinematicProject
    ) -> Dict[str, str]:
        """
        Generate start and end frame images using Nano Banana Pro

        Args:
            scene: Compiled CinematicScene
            project: CinematicProject

        Returns:
            Dict with {"start_frame_url": "...", "end_frame_url": "..."}
        """
        if not scene.start_frame_prompt or not scene.end_frame_prompt:
            raise ValueError("Scene must be compiled before generating images")

        print(f"🖼️  Generating frame images for scene {scene.sequence_number}...")

        # Use existing Nano Banana integration
        from studio.providers.kieai_provider import KieAIProvider

        provider = KieAIProvider(api_key=self.api_key)

        # Generate start frame
        print("   → Generating start frame...")
        start_url = provider.generate_image(
            prompt=scene.start_frame_prompt.full_prompt,
            model="nano-banana-pro",
            resolution=project.target_resolution
        )

        # Generate end frame
        print("   → Generating end frame...")
        end_url = provider.generate_image(
            prompt=scene.end_frame_prompt.full_prompt,
            model="nano-banana-pro",
            resolution=project.target_resolution
        )

        print(f"✅ Frame images generated")

        return {
            "start_frame_url": start_url,
            "end_frame_url": end_url
        }

    def generate_video(
        self,
        scene: CinematicScene,
        project: CinematicProject,
        start_frame_url: Optional[str] = None
    ) -> str:
        """
        Generate video using Veo 3

        Args:
            scene: Compiled CinematicScene
            project: CinematicProject
            start_frame_url: Optional reference image URL for start frame

        Returns:
            Video URL
        """
        if not scene.end_frame_prompt:
            raise ValueError("Scene must be compiled before generating video")

        print(f"🎬 Generating video for scene {scene.sequence_number}...")
        print(f"   Duration: {scene.duration_seconds}s")
        print(f"   Resolution: {project.target_resolution}")
        print(f"   FPS: {project.target_fps}")

        # Use existing Veo 3 integration
        from studio.providers.kieai_provider import KieAIProvider

        provider = KieAIProvider(api_key=self.api_key)

        # Generate video
        video_url = provider.generate_video(
            prompt=scene.end_frame_prompt.full_prompt,
            model="veo-3",
            duration=scene.duration_seconds,
            resolution=project.target_resolution,
            fps=project.target_fps,
            reference_image_url=start_frame_url
        )

        print(f"✅ Video generated: {video_url}")

        return video_url

    def generate_scene_full(
        self,
        scene: CinematicScene,
        project: CinematicProject
    ) -> Dict[str, Any]:
        """
        Generate both frame images and video for a scene

        Args:
            scene: Compiled CinematicScene
            project: CinematicProject

        Returns:
            Dict with all generated URLs
        """
        print(f"\n{'='*60}")
        print(f"GENERATING SCENE {scene.sequence_number}")
        print(f"{'='*60}\n")

        # Step 1: Generate frame images
        frames = self.generate_frame_images(scene, project)

        # Step 2: Generate video using start frame as reference
        video_url = self.generate_video(
            scene,
            project,
            start_frame_url=frames["start_frame_url"]
        )

        result = {
            "scene_id": scene.scene_id,
            "sequence_number": scene.sequence_number,
            "start_frame_url": frames["start_frame_url"],
            "end_frame_url": frames["end_frame_url"],
            "video_url": video_url,
            "duration_seconds": scene.duration_seconds
        }

        print(f"\n{'='*60}")
        print(f"✅ SCENE {scene.sequence_number} COMPLETE")
        print(f"{'='*60}\n")

        return result

    def generate_project_full(
        self,
        project: CinematicProject
    ) -> list[Dict[str, Any]]:
        """
        Generate videos for all scenes in project

        Args:
            project: Compiled CinematicProject

        Returns:
            List of generation results per scene
        """
        if not project.compilation_complete:
            raise ValueError("Project must be fully compiled before generation")

        print(f"\n{'#'*80}")
        print(f"GENERATING FULL PROJECT: {project.title}")
        print(f"{len(project.scenes)} scenes to generate")
        print(f"{'#'*80}\n")

        results = []

        for scene in project.scenes:
            result = self.generate_scene_full(scene, project)
            results.append(result)

        print(f"\n{'#'*80}")
        print(f"✨ PROJECT GENERATION COMPLETE: {project.title}")
        print(f"{'#'*80}\n")

        return results
