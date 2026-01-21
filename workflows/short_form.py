"""
Short-Form Workflow
Orchestrates pipeline for short-form video generation.
"""

import uuid
from datetime import datetime
from typing import Dict, List
from core import ConfigManager, StateManager, CostTracker, AsyncOrchestrator
from modules import ShortsGenerator


class ShortFormWorkflow:
    """
    Complete workflow for short-form video generation.

    Pipeline:
    1. Generate multiple shorts (parallel)
    2. Optimize for platform
    3. Mark for upload
    """

    def __init__(
        self,
        config: ConfigManager,
        state: StateManager,
        cost_tracker: CostTracker,
        orchestrator: AsyncOrchestrator,
        shorts_generator: ShortsGenerator
    ):
        """Initialize workflow."""
        self.config = config
        self.state = state
        self.cost_tracker = cost_tracker
        self.orchestrator = orchestrator
        self.shorts_gen = shorts_generator

    async def execute(
        self,
        channel_id: str,
        num_shorts: int = None,
        scheduled_time: datetime = None
    ) -> List[str]:
        """
        Execute short-form workflow.

        Args:
            channel_id: Channel ID
            num_shorts: Number of shorts to generate (uses channel config if None)
            scheduled_time: Scheduled upload time

        Returns:
            List of video_ids for generated shorts
        """
        # Get channel config
        channel_config = self.config.get_channel(channel_id)
        if not channel_config:
            raise ValueError(f"Channel {channel_id} not found")

        # Check budget
        allowed, message = self.cost_tracker.check_budget_limit(channel_id)
        if not allowed:
            raise ValueError(f"Budget exceeded: {message}")

        # Determine number of shorts
        if num_shorts is None:
            num_shorts = channel_config.shorts_per_day

        print(f"\n{'='*60}")
        print(f"Starting short-form workflow for: {channel_config.channel_name}")
        print(f"Generating {num_shorts} shorts")
        print(f"{'='*60}\n")

        video_ids = []

        try:
            # Generate shorts
            print(f"Generating {num_shorts} standalone shorts...")
            short_paths = await self.shorts_gen.generate_standalone_shorts(
                channel_config=channel_config.__dict__,
                num_shorts=num_shorts
            )

            # Process each short
            for i, short_path in enumerate(short_paths):
                if short_path:
                    video_id = f"short_{channel_id}_{uuid.uuid4().hex[:8]}"

                    # Create record
                    self.state.create_video(
                        video_id=video_id,
                        channel_id=channel_id,
                        content_type='short_form',
                        scheduled_upload_time=scheduled_time,
                        metadata={'short_number': i+1}
                    )

                    # Optimize for platform
                    optimized_path = await self.shorts_gen.optimize_for_platform(
                        short_path=short_path,
                        platform='youtube_shorts'
                    )

                    # Store asset
                    self.state.add_asset(
                        asset_id=f"{video_id}_final",
                        video_id=video_id,
                        asset_type='final_video',
                        file_path=optimized_path
                    )

                    # Mark for upload
                    self.state.update_video_status(video_id, 'upload_pending')

                    video_ids.append(video_id)
                    print(f"✓ Short {i+1}/{num_shorts} complete: {video_id}")

            # Calculate costs
            for video_id in video_ids:
                cost = self.cost_tracker.get_video_cost(video_id)
                print(f"  Cost: ${cost:.2f}")

            print(f"\n{'='*60}")
            print(f"✓ SHORT-FORM WORKFLOW COMPLETE")
            print(f"Generated {len(video_ids)} shorts")
            print(f"{'='*60}\n")

            return video_ids

        except Exception as e:
            print(f"\n✗ Workflow failed: {e}")
            raise
