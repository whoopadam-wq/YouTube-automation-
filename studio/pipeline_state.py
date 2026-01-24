"""
Pipeline State Manager
Single source of truth for video production state
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict


class PipelineStage(Enum):
    """Pipeline stages - MUST be executed in order"""
    TOPIC_DISCOVERY = "topic_discovery"
    SCRIPT_GENERATION = "script_generation"
    SCENE_DECOMPOSITION = "scene_decomposition"
    CHARACTER_LOCK = "character_lock"
    LIGHTING_PLANNING = "lighting_planning"
    COMPOSITION_PLANNING = "composition_planning"
    MOTION_GRAPHICS_PLANNING = "motion_graphics_planning"
    CLIP_GENERATION = "clip_generation"
    EDITOR_ASSEMBLY = "editor_assembly"
    FINAL_REVIEW = "final_review"
    AUTO_PUBLISH = "auto_publish"
    COMPLETE = "complete"


class StageStatus(Enum):
    """Status of a pipeline stage"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SceneData:
    """Data for a single scene"""
    scene_id: str
    script_excerpt: str
    start_frame_prompt: Optional[str] = None
    start_frame_image: Optional[str] = None
    end_frame_prompt: Optional[str] = None
    end_frame_image: Optional[str] = None
    clip_output_path: Optional[str] = None
    agent_prompts: Dict[str, str] = None
    agent_outputs: Dict[str, Any] = None
    status: str = "pending"
    duration_seconds: float = 3.0

    def __post_init__(self):
        if self.agent_prompts is None:
            self.agent_prompts = {}
        if self.agent_outputs is None:
            self.agent_outputs = {}


@dataclass
class VideoProductionState:
    """Complete state for a single video production"""
    video_id: str
    created_at: str
    updated_at: str

    # Metadata
    title: str
    topic: str
    niche: str
    duration_target: float

    # Current pipeline stage
    current_stage: str  # PipelineStage value
    stage_statuses: Dict[str, Any]  # stage -> {status, ...data}

    # Content
    full_script: Optional[str] = None
    scenes: List[Dict] = None  # List of SceneData dicts

    # Characters
    characters: List[Dict] = None

    # Output
    final_video_path: Optional[str] = None
    final_thumbnail_path: Optional[str] = None

    # Publishing
    published_platforms: List[str] = None
    youtube_video_id: Optional[str] = None

    # Tracking
    cost_usd: float = 0.0
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.scenes is None:
            self.scenes = []
        if self.characters is None:
            self.characters = []
        if self.published_platforms is None:
            self.published_platforms = []
        if self.stage_statuses is None:
            self.stage_statuses = {stage.value: {"status": StageStatus.PENDING.value} for stage in PipelineStage}


class PipelineStateManager:
    """
    Manages pipeline state persistence
    Single source of truth for all video productions
    """

    def __init__(self, data_dir: str = "data/pipeline"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.index_file = os.path.join(data_dir, "index.json")
        self._ensure_index()

    def _ensure_index(self):
        """Ensure index file exists"""
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump({"videos": []}, f)

    def create_video(
        self,
        title: str,
        topic: str,
        niche: str,
        duration_target: float
    ) -> VideoProductionState:
        """Create a new video production"""
        video_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.now().isoformat()

        state = VideoProductionState(
            video_id=video_id,
            created_at=now,
            updated_at=now,
            title=title,
            topic=topic,
            niche=niche,
            duration_target=duration_target,
            current_stage=PipelineStage.TOPIC_DISCOVERY.value,
            stage_statuses={stage.value: {"status": StageStatus.PENDING.value} for stage in PipelineStage}
        )

        self.save_state(state)
        self._add_to_index(video_id)

        print(f"✅ Created video production: {video_id}")
        print(f"   Title: {title}")
        print(f"   Topic: {topic}")
        print(f"   Duration: {duration_target}s")

        return state

    def save_state(self, state: VideoProductionState):
        """Save video state to disk"""
        state.updated_at = datetime.now().isoformat()

        state_file = os.path.join(self.data_dir, f"{state.video_id}.json")
        with open(state_file, 'w') as f:
            json.dump(asdict(state), f, indent=2)

    def load_state(self, video_id: str) -> Optional[VideoProductionState]:
        """Load video state from disk"""
        state_file = os.path.join(self.data_dir, f"{video_id}.json")
        if not os.path.exists(state_file):
            return None

        with open(state_file, 'r') as f:
            data = json.load(f)

        return VideoProductionState(**data)

    def list_videos(
        self,
        stage: Optional[PipelineStage] = None,
        status: Optional[StageStatus] = None
    ) -> List[VideoProductionState]:
        """List all videos, optionally filtered"""
        with open(self.index_file, 'r') as f:
            index = json.load(f)

        videos = []
        for video_id in index["videos"]:
            state = self.load_state(video_id)
            if state:
                if stage and state.current_stage != stage.value:
                    continue
                if status:
                    current_stage_data = state.stage_statuses.get(state.current_stage, {})
                    current_status = current_stage_data.get("status") if isinstance(current_stage_data, dict) else current_stage_data
                    if current_status != status.value:
                        continue
                videos.append(state)

        return videos

    def update_stage(
        self,
        video_id: str,
        stage: PipelineStage,
        status: StageStatus,
        data: Optional[Dict] = None
    ):
        """Update stage status and optionally add data"""
        state = self.load_state(video_id)
        if not state:
            raise ValueError(f"Video {video_id} not found")

        # Initialize stage data dict if it doesn't exist or is just a string (old format)
        if not isinstance(state.stage_statuses.get(stage.value), dict):
            state.stage_statuses[stage.value] = {}

        # Update status
        state.stage_statuses[stage.value]["status"] = status.value

        # Add any additional data to the stage dict
        if data:
            state.stage_statuses[stage.value].update(data)

        if status == StageStatus.COMPLETED:
            # Move to next stage
            next_stage = self._get_next_stage(stage)
            if next_stage:
                state.current_stage = next_stage.value
                if next_stage.value not in state.stage_statuses or not isinstance(state.stage_statuses[next_stage.value], dict):
                    state.stage_statuses[next_stage.value] = {}
                state.stage_statuses[next_stage.value]["status"] = StageStatus.PENDING.value
            else:
                state.current_stage = PipelineStage.COMPLETE.value

        if status == StageStatus.FAILED and data and 'error' in data:
            state.error_message = data['error']

        # Also update state attributes if they exist (for backward compatibility)
        if data:
            for key, value in data.items():
                if hasattr(state, key):
                    setattr(state, key, value)

        self.save_state(state)

        print(f"   📊 Stage {stage.value}: {status.value}")

    def add_scene(
        self,
        video_id: str,
        scene_data: SceneData
    ):
        """Add a scene to the video"""
        state = self.load_state(video_id)
        if not state:
            raise ValueError(f"Video {video_id} not found")

        state.scenes.append(asdict(scene_data))
        self.save_state(state)

    def update_scene(
        self,
        video_id: str,
        scene_id: str,
        updates: Dict
    ):
        """Update a specific scene"""
        state = self.load_state(video_id)
        if not state:
            raise ValueError(f"Video {video_id} not found")

        for scene in state.scenes:
            if scene['scene_id'] == scene_id:
                scene.update(updates)
                break

        self.save_state(state)

    def get_progress(self, video_id: str) -> Dict[str, Any]:
        """Get production progress"""
        state = self.load_state(video_id)
        if not state:
            return {}

        total_stages = len(PipelineStage) - 1  # Exclude COMPLETE
        completed_stages = sum(
            1 for stage_data in state.stage_statuses.values()
            if (isinstance(stage_data, dict) and stage_data.get("status") == StageStatus.COMPLETED.value) or
               (isinstance(stage_data, str) and stage_data == StageStatus.COMPLETED.value)
        )

        return {
            "video_id": video_id,
            "title": state.title,
            "current_stage": state.current_stage,
            "progress_percentage": int((completed_stages / total_stages) * 100),
            "completed_stages": completed_stages,
            "total_stages": total_stages,
            "scenes_count": len(state.scenes),
            "cost_usd": state.cost_usd,
            "error": state.error_message
        }

    def _get_next_stage(self, current: PipelineStage) -> Optional[PipelineStage]:
        """Get next pipeline stage"""
        stages = list(PipelineStage)
        try:
            current_idx = stages.index(current)
            if current_idx < len(stages) - 1:
                return stages[current_idx + 1]
        except ValueError:
            pass
        return None

    def _add_to_index(self, video_id: str):
        """Add video to index"""
        with open(self.index_file, 'r') as f:
            index = json.load(f)

        if video_id not in index["videos"]:
            index["videos"].append(video_id)

        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
