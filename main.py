#!/usr/bin/env python3
"""
AI Content Automation Exoskeleton
Main entry point and CLI interface.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import ConfigManager, StateManager, CostTracker, AsyncOrchestrator
from modules import (
    ScriptGenerator,
    CharacterCreator,
    AnchorCharacterManager,
    ScenePlanner,
    MediaGenerator,
    VideoAssembler,
    ShortsGenerator,
    Scheduler
)
from workflows import LongFormWorkflow, ShortFormWorkflow


class AutomationSystem:
    """
    Main automation system orchestrator.
    """

    def __init__(self):
        """Initialize system."""
        print("Initializing AI Content Automation System...")

        # Core components
        self.config = ConfigManager()
        self.state = StateManager(self.config)
        self.cost_tracker = CostTracker(self.config)
        self.orchestrator = AsyncOrchestrator(self.config)

        # Modules
        self.script_gen = ScriptGenerator(self.config, self.cost_tracker)
        self.char_creator = CharacterCreator(self.config, self.cost_tracker)
        self.anchor_mgr = AnchorCharacterManager(self.config, self.cost_tracker)
        self.scene_planner = ScenePlanner(self.config, self.cost_tracker)
        self.media_gen = MediaGenerator(self.config, self.cost_tracker, self.orchestrator)
        self.video_assembler = VideoAssembler(self.config, self.cost_tracker)

        # Shorts generator
        self.shorts_gen = ShortsGenerator(
            self.config,
            self.cost_tracker,
            self.script_gen,
            self.media_gen,
            self.video_assembler
        )

        # Workflows
        self.long_form_workflow = LongFormWorkflow(
            self.config,
            self.state,
            self.cost_tracker,
            self.orchestrator
        )

        self.short_form_workflow = ShortFormWorkflow(
            self.config,
            self.state,
            self.cost_tracker,
            self.orchestrator,
            self.shorts_gen
        )

        # Scheduler
        self.scheduler = Scheduler(self.config, self.state, self.cost_tracker)

        print("✓ System initialized")
        print(f"✓ Loaded {len(self.config.channels)} channels")
        print(f"✓ {len(self.config.get_active_channels())} active channels\n")

    async def generate_long_form(self, channel_id: str):
        """Generate long-form content for a channel."""
        return await self.long_form_workflow.execute(
            channel_id=channel_id,
            scheduled_time=datetime.now()
        )

    async def generate_short_form(self, channel_id: str):
        """Generate short-form content for a channel."""
        channel = self.config.get_channel(channel_id)
        num_shorts = channel.shorts_per_day if channel else 3

        return await self.short_form_workflow.execute(
            channel_id=channel_id,
            num_shorts=num_shorts,
            scheduled_time=datetime.now()
        )

    def start_scheduler(self):
        """Start automated scheduler."""
        print("Setting up schedules...")

        self.scheduler.setup_channel_schedules(
            long_form_callback=self.generate_long_form,
            short_form_callback=self.generate_short_form
        )

        summary = self.scheduler.get_schedule_summary()
        print(f"\nSchedule Summary:")
        print(f"  Total Jobs: {summary['total_jobs']}")
        print(f"  Active Channels: {summary['channels']}")
        print(f"\nNext Runs:")
        for run in summary['next_runs']:
            print(f"  - {run['next_run']}: {run['job']}")

        print("\nStarting scheduler...")
        self.scheduler.run_forever()

    def show_status(self):
        """Show system status."""
        print("\n" + "="*60)
        print("SYSTEM STATUS")
        print("="*60)

        # Active channels
        print("\nActive Channels:")
        for channel in self.config.get_active_channels():
            print(f"  - {channel.channel_name} ({channel.channel_id})")
            print(f"    Niche: {channel.niche}")
            print(f"    Long-form: {channel.long_form_enabled}")
            print(f"    Shorts: {channel.shorts_enabled} ({channel.shorts_per_day}/day)")
            print(f"    Daily Budget: ${channel.api_cost_cap_per_day:.2f}")

        # Cost summary
        print("\nCost Summary (Today):")
        total_today = self.cost_tracker.get_global_costs_today()
        print(f"  Total: ${total_today:.2f}")

        for channel in self.config.get_active_channels():
            channel_cost = self.cost_tracker.get_channel_costs_today(channel.channel_id)
            print(f"  {channel.channel_name}: ${channel_cost:.2f} / ${channel.api_cost_cap_per_day:.2f}")

        # Alerts
        alerts = self.cost_tracker.get_alerts()
        if alerts:
            print("\n⚠ Cost Alerts:")
            for alert in alerts:
                print(f"  {alert['channel_name']}: {alert['percentage']:.1f}% of daily budget")

        print("\n" + "="*60 + "\n")

    def list_channels(self):
        """List all configured channels."""
        print("\n" + "="*60)
        print("CONFIGURED CHANNELS")
        print("="*60 + "\n")

        for channel in self.config.channels:
            status_icon = "✓" if channel.status == "active" else "⏸"
            print(f"{status_icon} {channel.channel_name}")
            print(f"  ID: {channel.channel_id}")
            print(f"  Status: {channel.status}")
            print(f"  Niche: {channel.niche}")
            print(f"  Long-form: {channel.long_form_enabled}")
            print(f"  Shorts: {channel.shorts_enabled}")
            print()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI Content Automation Exoskeleton',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start automated scheduler
  python main.py schedule

  # Generate long-form video for a channel
  python main.py generate-long <channel_id>

  # Generate shorts for a channel
  python main.py generate-shorts <channel_id>

  # Show system status
  python main.py status

  # List all channels
  python main.py list-channels
        """
    )

    parser.add_argument(
        'command',
        choices=['schedule', 'generate-long', 'generate-shorts', 'status', 'list-channels'],
        help='Command to execute'
    )

    parser.add_argument(
        'channel_id',
        nargs='?',
        help='Channel ID (required for generate commands)'
    )

    args = parser.parse_args()

    # Initialize system
    system = AutomationSystem()

    # Execute command
    if args.command == 'schedule':
        system.start_scheduler()

    elif args.command == 'generate-long':
        if not args.channel_id:
            print("Error: channel_id required for generate-long")
            sys.exit(1)

        video_id = await system.generate_long_form(args.channel_id)
        print(f"\n✓ Video generated: {video_id}")

    elif args.command == 'generate-shorts':
        if not args.channel_id:
            print("Error: channel_id required for generate-shorts")
            sys.exit(1)

        video_ids = await system.generate_short_form(args.channel_id)
        print(f"\n✓ Generated {len(video_ids)} shorts")

    elif args.command == 'status':
        system.show_status()

    elif args.command == 'list-channels':
        system.list_channels()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown requested. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
