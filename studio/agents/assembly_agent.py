"""
Assembly Agent - Seventh and final agent in the pipeline
Assembles all clips into final video using Remotion
"""
import os
import json
import subprocess
from typing import List
from pathlib import Path
from studio.schemas import SceneClip, ProductionJob


class AssemblyAgent:
    """
    Uses Remotion to assemble final video from all clips
    - Syncs video clips with audio narration
    - Adds captions/subtitles
    - Handles transitions
    - Renders in multiple formats (16:9, 9:16, 1:1)
    """

    def __init__(self):
        self.remotion_root = Path(__file__).parent.parent / "remotion"
        self.output_dir = Path("data/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

    async def assemble_video(self, job: ProductionJob, clips: List[SceneClip]) -> ProductionJob:
        """
        Assemble all clips into final video

        Args:
            job: ProductionJob
            clips: List of SceneClip objects with video_url and audio_url

        Returns:
            Updated job with final_video_path and final_video_url
        """
        print(f"🎬 Assembly Agent: Assembling {len(clips)} clips into final video...")

        # Validate all clips are ready
        missing_videos = [c for c in clips if not c.video_url or c.video_status != "complete"]
        if missing_videos:
            raise ValueError(f"{len(missing_videos)} clips missing video")

        # Create Remotion composition data
        composition_data = self._create_composition_data(job, clips)

        # Write composition to JSON file
        composition_file = self.output_dir / f"{job.job_id}_composition.json"
        with open(composition_file, 'w') as f:
            json.dump(composition_data, f, indent=2)

        print(f"   📝 Created composition: {composition_file}")

        # Determine output format based on platform
        aspect_ratio = self._get_aspect_ratio(job.platform)
        output_file = self.output_dir / f"{job.job_id}_{aspect_ratio}.mp4"

        if self.use_mock:
            # Mock assembly for testing
            job.final_video_path = str(output_file)
            job.final_video_url = f"https://mock-storage.example.com/{output_file.name}"
            print(f"✅ Assembly Agent: Mock assembly complete")
            return job

        # Render with Remotion
        try:
            self._render_with_remotion(
                composition_file=composition_file,
                output_file=output_file,
                aspect_ratio=aspect_ratio
            )

            job.final_video_path = str(output_file)
            job.final_video_url = f"https://storage.example.com/{output_file.name}"  # TODO: Upload to real storage

            print(f"✅ Assembly Agent: Video assembled -> {output_file}")

        except Exception as e:
            print(f"❌ Assembly Agent: Remotion render failed: {e}")
            raise

        return job

    def _create_composition_data(self, job: ProductionJob, clips: List[SceneClip]) -> dict:
        """Create Remotion composition data structure"""
        composition = {
            "version": "1.0",
            "title": job.title,
            "fps": 30,
            "durationInFrames": int(sum(c.duration for c in clips) * 30),
            "width": 1920,
            "height": 1080,
            "clips": []
        }

        current_frame = 0
        for clip in clips:
            clip_data = {
                "id": clip.clip_id,
                "sequence": clip.sequence_number,
                "startFrame": current_frame,
                "durationInFrames": int(clip.duration * 30),
                "videoUrl": clip.video_url,
                "audioUrl": clip.audio_url,
                "transition": clip.frame_spec.transition_type if clip.frame_spec else "cut",
                "captions": {
                    "text": clip.narration_text,
                    "style": "bottom-third",
                    "enabled": job.platform in ["tiktok", "instagram"]  # Captions for social
                }
            }
            composition["clips"].append(clip_data)
            current_frame += clip_data["durationInFrames"]

        return composition

    def _get_aspect_ratio(self, platform: str) -> str:
        """Get aspect ratio for platform"""
        if platform in ["tiktok", "instagram"]:
            return "9:16"  # Vertical
        elif platform == "youtube":
            return "16:9"  # Horizontal
        else:
            return "16:9"  # Default

    def _render_with_remotion(self, composition_file: Path, output_file: Path, aspect_ratio: str):
        """
        Render video using Remotion CLI

        This assumes Remotion is set up in the studio/remotion directory
        """
        # Set dimensions based on aspect ratio
        dimensions = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1080, 1080)
        }
        width, height = dimensions.get(aspect_ratio, (1920, 1080))

        # Build Remotion render command
        # Note: This requires Remotion to be installed and configured
        cmd = [
            "npx", "remotion", "render",
            str(self.remotion_root / "src" / "index.tsx"),
            "VideoComposition",
            str(output_file),
            "--props", str(composition_file),
            "--width", str(width),
            "--height", str(height),
            "--codec", "h264",
            "--overwrite"
        ]

        print(f"   🎬 Rendering with Remotion: {' '.join(cmd)}")

        # Run Remotion render
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.remotion_root)
        )

        if result.returncode != 0:
            raise RuntimeError(f"Remotion render failed: {result.stderr}")

        print(f"   ✅ Remotion render complete")


class CaptionGenerator:
    """
    Generates caption/subtitle files for videos
    """

    def __init__(self):
        pass

    async def generate_captions(self, clips: List[SceneClip]) -> dict:
        """
        Generate SRT captions from narration text

        Returns:
            Caption data with timing information
        """
        captions = []
        current_time = 0.0

        for clip in clips:
            if clip.narration_text:
                caption = {
                    "index": clip.sequence_number,
                    "start": current_time,
                    "end": current_time + clip.duration,
                    "text": clip.narration_text
                }
                captions.append(caption)

            current_time += clip.duration

        return {"captions": captions}

    def export_srt(self, captions: dict, output_path: str):
        """Export captions as SRT file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, caption in enumerate(captions['captions'], 1):
                f.write(f"{i}\n")
                f.write(f"{self._format_time(caption['start'])} --> {self._format_time(caption['end'])}\n")
                f.write(f"{caption['text']}\n\n")

    def _format_time(self, seconds: float) -> str:
        """Format seconds as SRT time (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
