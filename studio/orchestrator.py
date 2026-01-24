"""
Agent Orchestration Engine
Runs agents sequentially with Review/Auto modes
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from studio.schemas import ProductionJob, ProductionMode, AgentStage, SceneClip
from studio.agents.script_agent import ScriptAgent
from studio.agents.character_lock_agent import CharacterLockAgent
from studio.agents.lighting_agent import LightingAgent
from studio.agents.composition_agent import CompositionAgent
from studio.agents.frame_agent import FrameAgent
from studio.agents.video_agent import VideoAgent, AudioAgent
from studio.agents.assembly_agent import AssemblyAgent


class ProductionOrchestrator:
    """
    Orchestrates the sequential agent pipeline
    Supports Review mode (stop after each agent) and Auto mode (run all)
    """

    def __init__(self):
        # Initialize all agents
        self.script_agent = ScriptAgent()
        self.character_agent = CharacterLockAgent()
        self.lighting_agent = LightingAgent()
        self.composition_agent = CompositionAgent()
        self.frame_agent = FrameAgent()
        self.video_agent = VideoAgent()
        self.audio_agent = AudioAgent()
        self.assembly_agent = AssemblyAgent()

        # Job storage directory (persisted to disk)
        self.jobs_dir = Path("data/studio_jobs")
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

        # Load existing jobs from disk
        self.jobs = {}
        self._load_jobs_from_disk()

    def _load_jobs_from_disk(self):
        """Load all saved jobs from disk"""
        print(f"📂 Loading jobs from {self.jobs_dir}")
        for job_file in self.jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                    job = ProductionJob.from_dict(job_data)
                    self.jobs[job.job_id] = job
                    print(f"   ✅ Loaded job: {job.job_id} - {job.title}")
            except Exception as e:
                print(f"   ❌ Failed to load {job_file.name}: {e}")

        print(f"📂 Loaded {len(self.jobs)} job(s) from disk\n")

    def _save_job_to_disk(self, job: ProductionJob):
        """Save a job to disk"""
        job_file = self.jobs_dir / f"{job.job_id}.json"
        try:
            with open(job_file, 'w') as f:
                json.dump(job.to_dict(), f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save job {job.job_id} to disk: {e}")

    async def create_job(
        self,
        channel_id: str,
        title: str,
        topic: str,
        duration_target: float,
        platform: str = "youtube",
        mode: ProductionMode = ProductionMode.AUTO,
        visual_style: str = "cinematic",
        tone: str = "engaging"
    ) -> ProductionJob:
        """
        Create a new production job

        Args:
            channel_id: Channel identifier
            title: Video title
            topic: Video topic/prompt
            duration_target: Target duration in seconds
            platform: Target platform (youtube, tiktok, instagram, all)
            mode: REVIEW (stop after each agent) or AUTO (run all)
            visual_style: Visual style
            tone: Tone/mood

        Returns:
            ProductionJob initialized at SCRIPT stage
        """
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        job = ProductionJob(
            job_id=job_id,
            channel_id=channel_id,
            created_at=datetime.now(),
            mode=mode,
            current_stage=AgentStage.SCRIPT,
            title=title,
            topic=topic,
            duration_target=duration_target,
            platform=platform,
            visual_style=visual_style,
            tone=tone
        )

        self.jobs[job_id] = job
        self._save_job_to_disk(job)  # Persist to disk

        print(f"\n{'='*60}")
        print(f"🎬 NEW PRODUCTION JOB: {job_id}")
        print(f"{'='*60}")
        print(f"Title: {title}")
        print(f"Platform: {platform}")
        print(f"Duration: {duration_target}s")
        print(f"Mode: {mode.value.upper()}")
        print(f"💾 Saved to: {self.jobs_dir / f'{job_id}.json'}")
        print(f"{'='*60}\n")

        return job

    async def run_pipeline(self, job_id: str, stop_at: Optional[AgentStage] = None) -> ProductionJob:
        """
        Run the production pipeline

        Args:
            job_id: Job identifier
            stop_at: Optional stage to stop at (for Review mode)

        Returns:
            Updated ProductionJob
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        print(f"\n🚀 Starting pipeline for job: {job_id}")
        print(f"   Current stage: {job.current_stage.value}")
        print(f"   Mode: {job.mode.value}")

        try:
            # Run agents sequentially - NO SKIPPING ALLOWED
            while job.current_stage != AgentStage.COMPLETE:
                print(f"\n{'─'*60}")
                print(f"▶️  STAGE: {job.current_stage.value.upper()}")
                print(f"{'─'*60}")

                # Run current stage
                await self._run_stage(job)

                # Check if we should stop (Review mode)
                if stop_at and job.current_stage == stop_at:
                    print(f"\n⏸️  Paused at {stop_at.value} (Review mode)")
                    break

                # Move to next stage
                next_stage = job.get_next_stage()
                if next_stage:
                    job.current_stage = next_stage
                else:
                    job.current_stage = AgentStage.COMPLETE
                    job.is_complete = True

                # Save job state after stage transition
                self._save_job_to_disk(job)

            if job.is_complete:
                print(f"\n{'='*60}")
                print(f"✅ PRODUCTION COMPLETE: {job.title}")
                print(f"{'='*60}")
                print(f"Final video: {job.final_video_path}")
                print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n❌ Pipeline failed at stage {job.current_stage.value}: {e}")
            job.error_message = str(e)
            self._save_job_to_disk(job)  # Save error state
            raise

        return job

    async def _run_stage(self, job: ProductionJob):
        """Run a single agent stage"""
        stage = job.current_stage

        if stage == AgentStage.SCRIPT:
            clips = await self.script_agent.generate_script(job)
            job.clips = clips

        elif stage == AgentStage.CHARACTER_LOCK:
            job = await self.character_agent.lock_characters(job, job.clips)

        elif stage == AgentStage.LIGHTING:
            job.clips = await self.lighting_agent.design_lighting(job, job.clips)

        elif stage == AgentStage.COMPOSITION:
            job.clips = await self.composition_agent.design_composition(job, job.clips)

        elif stage == AgentStage.FRAME:
            job.clips = await self.frame_agent.generate_frame_specs(job, job.clips)

        elif stage == AgentStage.VIDEO:
            # Generate both video and audio
            job.clips = await self.video_agent.generate_videos(job, job.clips)
            job.clips = await self.audio_agent.generate_audio(job, job.clips)

        elif stage == AgentStage.ASSEMBLY:
            job = await self.assembly_agent.assemble_video(job, job.clips)

        else:
            raise ValueError(f"Unknown stage: {stage}")

    async def continue_from_stage(self, job_id: str) -> ProductionJob:
        """
        Continue pipeline from current stage (after review)

        Args:
            job_id: Job identifier

        Returns:
            Updated ProductionJob
        """
        return await self.run_pipeline(job_id)

    def get_job(self, job_id: str) -> Optional[ProductionJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)

    def list_jobs(self) -> list:
        """List all jobs"""
        return [
            {
                "job_id": job.job_id,
                "title": job.title,
                "stage": job.current_stage.value,
                "progress": job.get_progress_percentage(),
                "is_complete": job.is_complete,
                "created_at": job.created_at.isoformat()
            }
            for job in self.jobs.values()
        ]

    async def regenerate_stage(self, job_id: str, stage: AgentStage) -> ProductionJob:
        """
        Regenerate a specific stage (useful for timeline editing)

        Args:
            job_id: Job identifier
            stage: Stage to regenerate

        Returns:
            Updated ProductionJob
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        print(f"\n🔄 Regenerating stage: {stage.value}")

        # Temporarily set current stage
        original_stage = job.current_stage
        job.current_stage = stage

        # Run stage
        await self._run_stage(job)

        # Restore original stage
        job.current_stage = original_stage

        print(f"✅ Stage {stage.value} regenerated")

        return job

    async def update_clip(self, job_id: str, clip_id: str, updates: dict) -> ProductionJob:
        """
        Update a specific clip (for timeline editing)

        Args:
            job_id: Job identifier
            clip_id: Clip identifier
            updates: Dictionary of fields to update

        Returns:
            Updated ProductionJob
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Find and update clip
        for clip in job.clips:
            if clip.clip_id == clip_id:
                for key, value in updates.items():
                    if hasattr(clip, key):
                        setattr(clip, key, value)
                print(f"✅ Updated clip {clip_id}: {updates}")
                break

        self._save_job_to_disk(job)  # Persist changes
        return job
