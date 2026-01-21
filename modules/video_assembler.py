"""
Video Assembler Module
Stitches together scenes, audio, music, and effects into final video.
"""

from typing import Dict, List, Any
from pathlib import Path
import subprocess
import json


class VideoAssembler:
    """
    Assembles final videos from components.
    Uses FFmpeg for video processing.
    """

    def __init__(self, config_manager, cost_tracker):
        """Initialize video assembler."""
        self.config = config_manager
        self.cost_tracker = cost_tracker
        self.temp_dir = config_manager.data_path / "temp"
        self.output_dir = config_manager.data_path / "output"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def assemble_video(
        self,
        scene_media: List[Dict],
        narration_audio: str,
        video_id: str,
        metadata: Dict[str, Any],
        background_music: str = None
    ) -> str:
        """
        Assemble final video from components.

        Args:
            scene_media: List of scene media assets
            narration_audio: Path to narration audio file
            video_id: Video ID
            metadata: Video metadata (title, description, etc.)
            background_music: Optional background music path

        Returns:
            Path to assembled video file
        """
        # Create concat file for FFmpeg
        concat_file = self.temp_dir / f"{video_id}_concat.txt"
        self._create_concat_file(scene_media, concat_file)

        # Output path
        output_path = self.output_dir / f"{video_id}.mp4"

        # FFmpeg command
        cmd = self._build_ffmpeg_command(
            concat_file=str(concat_file),
            narration_audio=narration_audio,
            background_music=background_music,
            output_path=str(output_path)
        )

        # Execute FFmpeg
        print(f"Assembling video: {video_id}")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Video assembled: {output_path}")
            return str(output_path)

        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise

    def _create_concat_file(
        self,
        scene_media: List[Dict],
        concat_file: Path
    ):
        """Create FFmpeg concat file."""
        with open(concat_file, 'w') as f:
            for scene in scene_media:
                video_path = scene.get('video_url') or scene.get('image_url')
                if video_path:
                    f.write(f"file '{video_path}'\n")

    def _build_ffmpeg_command(
        self,
        concat_file: str,
        narration_audio: str,
        background_music: str,
        output_path: str
    ) -> List[str]:
        """Build FFmpeg command."""
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-i', narration_audio,
        ]

        # Add background music if provided
        if background_music:
            cmd.extend(['-i', background_music])
            # Mix audio streams
            cmd.extend([
                '-filter_complex',
                '[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2,volume=2[aout]',
                '-map', '0:v',
                '-map', '[aout]'
            ])
        else:
            # Just narration
            cmd.extend([
                '-map', '0:v',
                '-map', '1:a'
            ])

        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-y',
            output_path
        ])

        return cmd

    async def add_intro_outro(
        self,
        main_video: str,
        intro_clip: str = None,
        outro_clip: str = None,
        video_id: str = None
    ) -> str:
        """Add intro and outro clips to video."""
        if not intro_clip and not outro_clip:
            return main_video

        output_path = self.output_dir / f"{video_id}_final.mp4"

        # Create concat file
        concat_file = self.temp_dir / f"{video_id}_full_concat.txt"
        with open(concat_file, 'w') as f:
            if intro_clip:
                f.write(f"file '{intro_clip}'\n")
            f.write(f"file '{main_video}'\n")
            if outro_clip:
                f.write(f"file '{outro_clip}'\n")

        # Concat videos
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)

    async def add_text_overlay(
        self,
        video_path: str,
        text: str,
        duration: float,
        position: str = "bottom"
    ) -> str:
        """Add text overlay to video."""
        output_path = self.temp_dir / f"overlay_{Path(video_path).name}"

        # Position mapping
        positions = {
            'top': 'x=(w-text_w)/2:y=50',
            'bottom': 'x=(w-text_w)/2:y=h-th-50',
            'center': 'x=(w-text_w)/2:y=(h-text_h)/2'
        }

        pos = positions.get(position, positions['bottom'])

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"drawtext=text='{text}':fontsize=48:fontcolor=white:{pos}:box=1:boxcolor=black@0.5",
            '-codec:a', 'copy',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)

    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds."""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])

    def cleanup_temp_files(self, video_id: str):
        """Clean up temporary files for a video."""
        for temp_file in self.temp_dir.glob(f"{video_id}*"):
            temp_file.unlink()
