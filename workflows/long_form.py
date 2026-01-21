"""
Long-Form Workflow
Orchestrates complete pipeline for long-form video generation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from core import ConfigManager, StateManager, CostTracker, AsyncOrchestrator
from modules import (
    ScriptGenerator,
    CharacterCreator,
    AnchorCharacterManager,
    ScenePlanner,
    MediaGenerator,
    VideoAssembler
)


class LongFormWorkflow:
    """
    Complete workflow for long-form video generation.

    Pipeline:
    1. Generate script
    2. Create characters
    3. Get/create anchor character
    4. Plan scenes
    5. Generate media (images + videos)
    6. Generate narration audio
    7. Assemble final video
    8. Mark for upload
    """

    def __init__(
        self,
        config: ConfigManager,
        state: StateManager,
        cost_tracker: CostTracker,
        orchestrator: AsyncOrchestrator
    ):
        """Initialize workflow with core components."""
        self.config = config
        self.state = state
        self.cost_tracker = cost_tracker
        self.orchestrator = orchestrator

        # Initialize modules
        self.script_gen = ScriptGenerator(config, cost_tracker)
        self.char_creator = CharacterCreator(config, cost_tracker)
        self.anchor_mgr = AnchorCharacterManager(config, cost_tracker)
        self.scene_planner = ScenePlanner(config, cost_tracker)
        self.media_gen = MediaGenerator(config, cost_tracker, orchestrator)
        self.video_assembler = VideoAssembler(config, cost_tracker)

    async def execute(
        self,
        channel_id: str,
        scheduled_time: datetime = None
    ) -> str:
        """
        Execute complete long-form workflow.

        Args:
            channel_id: Channel ID
            scheduled_time: Scheduled upload time

        Returns:
            video_id of generated content
        """
        # Get channel config
        channel_config = self.config.get_channel(channel_id)
        if not channel_config:
            raise ValueError(f"Channel {channel_id} not found")

        # Check budget
        allowed, message = self.cost_tracker.check_budget_limit(channel_id)
        if not allowed:
            raise ValueError(f"Budget exceeded: {message}")

        # Generate video ID
        video_id = f"long_{channel_id}_{uuid.uuid4().hex[:8]}"

        print(f"\n{'='*60}")
        print(f"Starting long-form workflow for: {channel_config.channel_name}")
        print(f"Video ID: {video_id}")
        print(f"{'='*60}\n")

        # Create video record
        self.state.create_video(
            video_id=video_id,
            channel_id=channel_id,
            content_type='long_form',
            scheduled_upload_time=scheduled_time,
            metadata={'channel_name': channel_config.channel_name}
        )

        try:
            # Step 1: Generate script
            print("Step 1/7: Generating script...")
            self.state.update_video_status(video_id, 'script_generation')
            stage_id = self.state.start_pipeline_stage(video_id, 'script_generation')

            script = await self.script_gen.generate_long_form_script(
                channel_config=channel_config.__dict__,
                video_id=video_id
            )

            self.state.complete_pipeline_stage(
                stage_id,
                success=True,
                output_data={'title': script.title, 'total_duration': script.total_duration}
            )
            print(f"✓ Script generated: {script.title} ({script.total_duration:.1f}s)")

            # Step 2: Create characters
            print("\nStep 2/7: Creating characters...")
            self.state.update_video_status(video_id, 'character_creation')
            stage_id = self.state.start_pipeline_stage(video_id, 'character_creation')

            characters = await self.char_creator.extract_and_create_characters(
                script=script.to_dict(),
                channel_config=channel_config.__dict__
            )

            self.state.complete_pipeline_stage(
                stage_id,
                success=True,
                output_data={'num_characters': len(characters)}
            )
            print(f"✓ Created {len(characters)} characters")

            # Step 3: Get anchor character
            print("\nStep 3/7: Loading anchor character...")
            anchor = await self.anchor_mgr.get_or_create_anchor(
                channel_config=channel_config.__dict__
            )

            if anchor:
                print(f"✓ Anchor character loaded: {anchor['name']}")
            else:
                print("✓ No anchor character for this channel")

            # Step 4: Plan scenes
            print("\nStep 4/7: Planning scenes...")
            self.state.update_video_status(video_id, 'scene_planning')
            stage_id = self.state.start_pipeline_stage(video_id, 'scene_planning')

            scene_plans = await self.scene_planner.plan_scenes(
                script=script.to_dict(),
                characters=[c.__dict__ for c in characters],
                channel_config=channel_config.__dict__
            )

            self.state.complete_pipeline_stage(
                stage_id,
                success=True,
                output_data={'num_scenes': len(scene_plans)}
            )
            print(f"✓ Planned {len(scene_plans)} scenes")

            # Step 5: Generate media
            print("\nStep 5/7: Generating media (images + videos)...")
            print("This may take several minutes...")
            self.state.update_video_status(video_id, 'media_generation')
            stage_id = self.state.start_pipeline_stage(video_id, 'media_generation')

            scene_media = await self.media_gen.generate_scene_media(
                scene_plans=[sp.__dict__ for sp in scene_plans],
                channel_config=channel_config.__dict__,
                video_id=video_id
            )

            self.state.complete_pipeline_stage(
                stage_id,
                success=True,
                output_data={'num_media_assets': len(scene_media)}
            )
            print(f"✓ Generated {len(scene_media)} media assets")

            # Step 6: Generate narration
            print("\nStep 6/7: Generating narration audio...")
            narration_audio = await self._generate_narration(
                script.scenes,
                channel_config.__dict__
            )
            print(f"✓ Narration generated")

            # Step 7: Assemble video
            print("\nStep 7/7: Assembling final video...")
            self.state.update_video_status(video_id, 'assembly')
            stage_id = self.state.start_pipeline_stage(video_id, 'assembly')

            final_video_path = await self.video_assembler.assemble_video(
                scene_media=scene_media,
                narration_audio=narration_audio,
                video_id=video_id,
                metadata={
                    'title': script.title,
                    'description': script.description
                }
            )

            self.state.complete_pipeline_stage(
                stage_id,
                success=True,
                output_data={'video_path': final_video_path}
            )
            print(f"✓ Video assembled: {final_video_path}")

            # Mark as ready for upload
            self.state.update_video_status(video_id, 'upload_pending')

            # Store video metadata
            self.state.add_asset(
                asset_id=f"{video_id}_final",
                video_id=video_id,
                asset_type='final_video',
                file_path=final_video_path,
                metadata={
                    'title': script.title,
                    'description': script.description,
                    'duration': script.total_duration
                }
            )

            # Calculate total cost
            total_cost = self.cost_tracker.get_video_cost(video_id)

            print(f"\n{'='*60}")
            print(f"✓ WORKFLOW COMPLETE")
            print(f"Video ID: {video_id}")
            print(f"Title: {script.title}")
            print(f"Duration: {script.total_duration:.1f}s")
            print(f"Total Cost: ${total_cost:.2f}")
            print(f"Output: {final_video_path}")
            print(f"{'='*60}\n")

            return video_id

        except Exception as e:
            print(f"\n✗ Workflow failed: {e}")
            self.state.update_video_status(video_id, 'failed', error_message=str(e))
            raise

    async def _generate_narration(
        self,
        scenes: list,
        channel_config: Dict[str, Any]
    ) -> str:
        """Generate narration audio for all scenes."""
        from api_providers import ElevenLabsProvider, OpenAIProvider

        provider_config = self.config.get_provider_config('voice_synthesis')
        provider_name = provider_config.get('primary', 'elevenlabs')
        api_key = self.config.get_api_key(provider_name)

        if provider_name == 'elevenlabs':
            provider = ElevenLabsProvider(api_key, provider_config)
        else:
            provider = OpenAIProvider(api_key, provider_config)

        # Combine all narration
        full_text = " ".join([scene.narration_text for scene in scenes])

        # Synthesize
        audio_path = await provider.synthesize_speech(
            text=full_text,
            voice_id=None
        )

        return audio_path
