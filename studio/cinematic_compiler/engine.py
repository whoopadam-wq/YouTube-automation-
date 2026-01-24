"""
Cinematic Production Compiler Engine
Core orchestrator for the 9-agent compilation pipeline
"""
import uuid
from datetime import datetime
from typing import List, Optional

from .schemas import (
    CinematicProject, CinematicScene, CompilerStage,
    CharacterIdentity
)
from .state_manager import CompilerStateManager
from .agents import (
    IdeaNarrativeAgent,
    SceneDecompositionAgent,
    CharacterIdentityAgent,
    SpatialTemporalAgent,
    CameraOpticsAgent,
    LightingPhysicsAgent,
    CompositionObservationAgent,
    MotionVFXAgent,
    PromptCompilerAgent
)


class CinematicCompiler:
    """
    CINEMATIC PRODUCTION COMPILER ENGINE

    A deterministic multi-agent system that operates as a COMPILER, not a writer.

    Architecture:
    Text → Structure → Identity → Space → Camera → Light → Motion → Continuity → Output Prompt

    Each transformation ADDS information. Nothing is overwritten unless explicitly instructed.
    Ambiguity is resolved once and then locked.

    Global Memory Rules:
    - Characters are immutable once defined
    - Locations are immutable once defined
    - Time-of-day is immutable per scene
    - Wardrobe is immutable unless explicitly changed
    - Facial identity NEVER changes
    - Physical proportions NEVER drift
    - Camera realism always overrides cinematic flair
    """

    def __init__(self, state_manager: Optional[CompilerStateManager] = None):
        """
        Initialize compiler engine

        Args:
            state_manager: Optional custom state manager (creates default if None)
        """
        self.state_manager = state_manager or CompilerStateManager()

        # Initialize 9 internal agents
        self.agents = {
            CompilerStage.IDEA_NARRATIVE: IdeaNarrativeAgent(),
            CompilerStage.SCENE_DECOMPOSITION: SceneDecompositionAgent(),
            CompilerStage.CHARACTER_IDENTITY: CharacterIdentityAgent(),
            CompilerStage.SPATIAL_TEMPORAL: SpatialTemporalAgent(),
            CompilerStage.CAMERA_OPTICS: CameraOpticsAgent(),
            CompilerStage.LIGHTING_PHYSICS: LightingPhysicsAgent(),
            CompilerStage.COMPOSITION: CompositionObservationAgent(),
            CompilerStage.MOTION_VFX: MotionVFXAgent(),
            CompilerStage.PROMPT_COMPILATION: PromptCompilerAgent()
        }

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("CINEMATIC PRODUCTION COMPILER v1.0")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("STATUS: READY")
        print("MODE: DETERMINISTIC COMPILATION")
        print("MEMORY: PERSISTENT")
        print("\nAGENT CHAIN LOADED:")
        for i, stage in enumerate(self.agents.keys(), 1):
            print(f" [{i}] {stage.value.replace('_', ' ').title():<25} → READY")
        print("\nGLOBAL MEMORY RULES: ENFORCED")
        print("ANTI-AI ENFORCEMENT: ACTIVE")
        print("CONTINUITY LOCKS: ENABLED")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    def create_project(
        self,
        title: str,
        target_platform: str = "veo3",
        visual_style_rules: str = ""
    ) -> CinematicProject:
        """
        Create a new cinematic project

        Args:
            title: Project title
            target_platform: "veo3", "nanoBanana", or "both"
            visual_style_rules: Global visual style constraints

        Returns:
            New CinematicProject
        """
        project_id = f"cin_{uuid.uuid4().hex[:12]}"

        project = CinematicProject(
            project_id=project_id,
            title=title,
            created_at=datetime.now(),
            target_platform=target_platform,
            visual_style_rules=visual_style_rules
        )

        # Save to persistent storage
        self.state_manager.save_project(project)

        print(f"✨ Project created: {title}")
        print(f"   ID: {project_id}")
        print(f"   Platform: {target_platform}")

        return project

    def load_project(self, project_id: str) -> Optional[CinematicProject]:
        """
        Load existing project from persistent storage

        Args:
            project_id: Project ID

        Returns:
            CinematicProject if found, None otherwise
        """
        return self.state_manager.load_project(project_id)

    def add_scene(
        self,
        project: CinematicProject,
        scene_description: str = "",
        duration_seconds: float = 5.0
    ) -> CinematicScene:
        """
        Add a new scene to project

        Args:
            project: CinematicProject
            scene_description: Initial scene description (optional)
            duration_seconds: Scene duration

        Returns:
            New CinematicScene added to project
        """
        scene_id = f"scene_{uuid.uuid4().hex[:8]}"
        sequence_number = len(project.scenes) + 1

        scene = CinematicScene(
            scene_id=scene_id,
            sequence_number=sequence_number,
            duration_seconds=duration_seconds
        )

        project.scenes.append(scene)

        # Save project
        self.state_manager.save_project(project)

        print(f"📍 Scene {sequence_number} added to project")

        return scene

    def compile_scene(
        self,
        project: CinematicProject,
        scene: CinematicScene,
        auto_save: bool = True
    ) -> CinematicScene:
        """
        Run scene through full 9-agent compilation pipeline

        Args:
            project: CinematicProject (for global context)
            scene: CinematicScene to compile
            auto_save: Save project after each agent (default: True)

        Returns:
            Fully compiled scene with start/end frame prompts
        """
        print(f"\n🎬 COMPILING SCENE {scene.sequence_number}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Run through all 9 agents sequentially
        for stage, agent in self.agents.items():
            print(f"\n[{stage.value.upper()}]")

            try:
                scene = agent.process(scene, project)

                if auto_save:
                    self.state_manager.save_project(project)

            except Exception as e:
                print(f"❌ ERROR in {agent.name}: {e}")
                raise

        # Mark as complete
        scene.locked = True

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✅ SCENE COMPILATION COMPLETE")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Final save
        if auto_save:
            self.state_manager.save_project(project)

        return scene

    def compile_project(self, project: CinematicProject) -> CinematicProject:
        """
        Compile all scenes in project

        Args:
            project: CinematicProject to compile

        Returns:
            Fully compiled project
        """
        print(f"\n🎥 COMPILING PROJECT: {project.title}")
        print(f"   {len(project.scenes)} scenes to compile\n")

        for scene in project.scenes:
            if not scene.locked:
                self.compile_scene(project, scene)

        project.compilation_complete = True
        project.current_stage = CompilerStage.COMPLETE

        self.state_manager.save_project(project)

        print("\n" + "=" * 80)
        print("✨ PROJECT COMPILATION COMPLETE")
        print("=" * 80)
        print(f"   Project: {project.title}")
        print(f"   Scenes: {len(project.scenes)}")
        print(f"   Characters: {len(project.global_characters)}")
        print(f"   Platform: {project.target_platform}")
        print("=" * 80 + "\n")

        return project

    def get_compiled_prompts(self, project: CinematicProject) -> List[dict]:
        """
        Extract all compiled prompts from project

        Args:
            project: CinematicProject

        Returns:
            List of dicts with scene prompts
        """
        prompts = []

        for scene in project.scenes:
            if scene.start_frame_prompt and scene.end_frame_prompt:
                prompts.append({
                    "scene_id": scene.scene_id,
                    "sequence_number": scene.sequence_number,
                    "duration": scene.duration_seconds,
                    "start_frame": scene.start_frame_prompt.full_prompt,
                    "end_frame": scene.end_frame_prompt.full_prompt,
                    "motion": scene.motion.motion_description if scene.motion else ""
                })

        return prompts

    def export_for_veo(self, project: CinematicProject) -> List[dict]:
        """
        Export prompts in Veo 3 API format

        Args:
            project: CinematicProject

        Returns:
            List of Veo API request payloads
        """
        veo_requests = []

        for scene in project.scenes:
            if scene.start_frame_prompt and scene.end_frame_prompt:
                veo_requests.append({
                    "scene_id": scene.scene_id,
                    "prompt": scene.end_frame_prompt.full_prompt,
                    "reference_image_prompt": scene.start_frame_prompt.full_prompt,
                    "duration_seconds": scene.duration_seconds,
                    "resolution": project.target_resolution,
                    "fps": project.target_fps
                })

        return veo_requests

    def export_for_nano_banana(self, project: CinematicProject) -> List[dict]:
        """
        Export prompts in Nano Banana API format

        Args:
            project: CinematicProject

        Returns:
            List of Nano Banana API request payloads
        """
        nb_requests = []

        for scene in project.scenes:
            if scene.start_frame_prompt:
                # Start frame image
                nb_requests.append({
                    "scene_id": scene.scene_id,
                    "frame_type": "start",
                    "prompt": scene.start_frame_prompt.full_prompt,
                    "resolution": project.target_resolution
                })

            if scene.end_frame_prompt:
                # End frame image
                nb_requests.append({
                    "scene_id": scene.scene_id,
                    "frame_type": "end",
                    "prompt": scene.end_frame_prompt.full_prompt,
                    "resolution": project.target_resolution
                })

        return nb_requests

    def lock_character(
        self,
        project: CinematicProject,
        character: CharacterIdentity
    ) -> bool:
        """
        Lock a character identity in project (immutable)

        Args:
            project: CinematicProject
            character: CharacterIdentity to lock

        Returns:
            True if locked successfully
        """
        return self.state_manager.lock_character(project.project_id, character)

    def list_projects(self) -> List[dict]:
        """
        List all projects

        Returns:
            List of project metadata
        """
        return self.state_manager.list_projects()

    def export_prompts_to_files(self, project: CinematicProject) -> str:
        """
        Export compiled prompts to text files

        Args:
            project: CinematicProject

        Returns:
            Path to export directory
        """
        return self.state_manager.export_prompts(project.project_id)
