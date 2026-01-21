"""
Scheduler Module
Manages scheduling and triggering of content generation.
"""

import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
import asyncio
import pytz


class Scheduler:
    """
    Manages content generation scheduling.
    Supports per-channel schedules and timezones.
    """

    def __init__(self, config_manager, state_manager, cost_tracker):
        """Initialize scheduler."""
        self.config = config_manager
        self.state = state_manager
        self.cost_tracker = cost_tracker
        self.jobs = []

    def setup_channel_schedules(
        self,
        long_form_callback: Callable,
        short_form_callback: Callable
    ):
        """
        Set up schedules for all active channels.

        Args:
            long_form_callback: Async function to call for long-form generation
            short_form_callback: Async function to call for short-form generation
        """
        schedule.clear()
        self.jobs = []

        for channel in self.config.get_active_channels():
            self._setup_channel_schedule(
                channel,
                long_form_callback,
                short_form_callback
            )

        print(f"Scheduled {len(self.jobs)} jobs across {len(self.config.get_active_channels())} channels")

    def _setup_channel_schedule(
        self,
        channel_config: Dict,
        long_form_callback: Callable,
        short_form_callback: Callable
    ):
        """Set up schedule for a single channel."""
        channel_id = channel_config['channel_id']
        timezone = pytz.timezone(channel_config.get('upload_timezone', 'UTC'))

        # Schedule long-form videos
        if channel_config.get('long_form_enabled', True):
            for schedule_item in channel_config.get('upload_schedule_long', []):
                time_str = schedule_item['time']
                days = schedule_item['days']

                for day in days:
                    job = self._schedule_task(
                        day=day,
                        time_str=time_str,
                        callback=long_form_callback,
                        channel_id=channel_id,
                        content_type='long_form',
                        timezone=timezone
                    )
                    self.jobs.append(job)

        # Schedule shorts
        if channel_config.get('shorts_enabled', True):
            for schedule_item in channel_config.get('upload_schedule_shorts', []):
                time_str = schedule_item['time']
                days = schedule_item['days']

                # Handle "daily" shorthand
                if 'daily' in [d.lower() for d in days]:
                    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

                for day in days:
                    job = self._schedule_task(
                        day=day,
                        time_str=time_str,
                        callback=short_form_callback,
                        channel_id=channel_id,
                        content_type='short_form',
                        timezone=timezone
                    )
                    self.jobs.append(job)

    def _schedule_task(
        self,
        day: str,
        time_str: str,
        callback: Callable,
        channel_id: str,
        content_type: str,
        timezone: pytz.timezone
    ):
        """Schedule a single task."""
        # Map day names to schedule functions
        day_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday,
        }

        day_scheduler = day_map.get(day.lower())
        if not day_scheduler:
            return None

        # Wrapper to handle async callbacks
        def job_wrapper():
            # Check budget before running
            allowed, message = self.cost_tracker.check_budget_limit(channel_id)
            if not allowed:
                print(f"Skipping {content_type} for {channel_id}: {message}")
                return

            # Run async callback
            asyncio.run(callback(channel_id, content_type))

        # Schedule job
        job = day_scheduler.at(time_str).do(job_wrapper)

        print(f"Scheduled {content_type} for {channel_id} on {day} at {time_str} ({timezone})")
        return job

    def run_forever(self):
        """Run scheduler forever."""
        print("Scheduler started. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\nScheduler stopped.")

    def run_once(self):
        """Run all pending jobs once (for testing)."""
        schedule.run_all()

    def get_next_runs(self, limit: int = 10) -> List[Dict]:
        """Get next scheduled runs."""
        upcoming = []

        for job in schedule.get_jobs()[:limit]:
            upcoming.append({
                'job': str(job),
                'next_run': job.next_run,
                'time_until': job.next_run - datetime.now() if job.next_run else None
            })

        return upcoming

    async def trigger_immediate_generation(
        self,
        channel_id: str,
        content_type: str,
        callback: Callable
    ):
        """Trigger immediate content generation (bypass schedule)."""
        # Check budget
        allowed, message = self.cost_tracker.check_budget_limit(channel_id)
        if not allowed:
            print(f"Cannot trigger generation: {message}")
            return None

        # Run callback
        return await callback(channel_id, content_type)

    def pause_channel(self, channel_id: str):
        """Pause all scheduled jobs for a channel."""
        # Remove jobs for this channel
        self.jobs = [
            job for job in self.jobs
            if channel_id not in str(job)
        ]
        print(f"Paused channel: {channel_id}")

    def resume_channel(
        self,
        channel_id: str,
        long_form_callback: Callable,
        short_form_callback: Callable
    ):
        """Resume scheduled jobs for a channel."""
        channel = self.config.get_channel(channel_id)
        if channel:
            self._setup_channel_schedule(
                channel,
                long_form_callback,
                short_form_callback
            )
            print(f"Resumed channel: {channel_id}")

    def get_schedule_summary(self) -> Dict[str, Any]:
        """Get summary of all schedules."""
        summary = {
            'total_jobs': len(schedule.get_jobs()),
            'channels': len(self.config.get_active_channels()),
            'next_runs': self.get_next_runs(5)
        }

        return summary
