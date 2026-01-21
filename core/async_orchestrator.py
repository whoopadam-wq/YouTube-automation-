"""
Async API Orchestrator
Reusable pattern for handling async API calls with polling, retries, and error handling.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, Awaitable
from enum import Enum
import aiohttp
from dataclasses import dataclass


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncTask:
    """Represents an async task being tracked."""
    task_id: str
    provider: str
    task_type: str
    status: TaskStatus
    created_at: float
    result_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AsyncOrchestrator:
    """
    Orchestrates async API calls with polling pattern.

    Universal pattern:
    1. Submit task → get task_id
    2. Poll status endpoint
    3. Wait with exponential backoff
    4. Fetch result when complete
    5. Handle errors and retries
    """

    def __init__(self, config_manager):
        """Initialize orchestrator."""
        self.config = config_manager
        self.active_tasks: Dict[str, AsyncTask] = {}

        # Get polling config
        polling_config = self.config.get_system_setting('async_polling', {})
        self.initial_delay = polling_config.get('initial_delay', 5)
        self.max_delay = polling_config.get('max_delay', 60)
        self.backoff_multiplier = polling_config.get('backoff_multiplier', 1.5)
        self.max_retries = polling_config.get('max_retries', 20)
        self.timeout = polling_config.get('timeout', 3600)

    async def submit_and_wait(
        self,
        submit_func: Callable[[], Awaitable[str]],
        poll_func: Callable[[str], Awaitable[Dict[str, Any]]],
        provider: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AsyncTask:
        """
        Universal async pattern.

        Args:
            submit_func: Async function that submits the task and returns task_id
            poll_func: Async function that polls status given task_id
            provider: Provider name (e.g., 'replicate', 'runway')
            task_type: Type of task (e.g., 'image_gen', 'video_gen')
            metadata: Optional metadata to attach to task

        Returns:
            AsyncTask with result or error
        """
        # Submit task
        task_id = await submit_func()

        # Create task tracker
        task = AsyncTask(
            task_id=task_id,
            provider=provider,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=time.time(),
            metadata=metadata or {}
        )

        self.active_tasks[task_id] = task

        # Poll until complete or timeout
        result = await self._poll_until_complete(task, poll_func)

        return result

    async def _poll_until_complete(
        self,
        task: AsyncTask,
        poll_func: Callable[[str], Awaitable[Dict[str, Any]]]
    ) -> AsyncTask:
        """
        Poll task until complete with exponential backoff.

        Args:
            task: The task to poll
            poll_func: Function to call for polling

        Returns:
            Updated task with result or error
        """
        delay = self.initial_delay
        attempts = 0
        start_time = time.time()

        while attempts < self.max_retries:
            # Check timeout
            if time.time() - start_time > self.timeout:
                task.status = TaskStatus.FAILED
                task.error = f"Timeout after {self.timeout}s"
                return task

            # Wait before polling
            await asyncio.sleep(delay)

            try:
                # Poll status
                status_data = await poll_func(task.task_id)

                # Update task status
                status = status_data.get('status', '').lower()

                if status in ['succeeded', 'completed', 'success']:
                    task.status = TaskStatus.SUCCEEDED
                    task.result_url = status_data.get('output') or status_data.get('url')
                    return task

                elif status in ['failed', 'error']:
                    task.status = TaskStatus.FAILED
                    task.error = status_data.get('error', 'Unknown error')
                    return task

                elif status in ['cancelled', 'canceled']:
                    task.status = TaskStatus.CANCELLED
                    task.error = "Task was cancelled"
                    return task

                else:
                    # Still processing
                    task.status = TaskStatus.PROCESSING

            except Exception as e:
                # Polling error - retry
                print(f"Polling error for {task.task_id}: {e}")

            # Exponential backoff
            delay = min(delay * self.backoff_multiplier, self.max_delay)
            attempts += 1

        # Max retries exceeded
        task.status = TaskStatus.FAILED
        task.error = f"Max polling attempts ({self.max_retries}) exceeded"
        return task

    async def submit_batch(
        self,
        tasks: list[Dict[str, Any]]
    ) -> list[AsyncTask]:
        """
        Submit multiple tasks in parallel.

        Args:
            tasks: List of task configurations, each containing:
                - submit_func
                - poll_func
                - provider
                - task_type
                - metadata (optional)

        Returns:
            List of completed AsyncTasks
        """
        # Create coroutines for all tasks
        coroutines = [
            self.submit_and_wait(
                submit_func=task['submit_func'],
                poll_func=task['poll_func'],
                provider=task['provider'],
                task_type=task['task_type'],
                metadata=task.get('metadata')
            )
            for task in tasks
        ]

        # Run all in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Convert exceptions to failed tasks
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed task
                failed_task = AsyncTask(
                    task_id=f"failed_{i}",
                    provider=tasks[i]['provider'],
                    task_type=tasks[i]['task_type'],
                    status=TaskStatus.FAILED,
                    created_at=time.time(),
                    error=str(result)
                )
                processed_results.append(failed_task)
            else:
                processed_results.append(result)

        return processed_results

    def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """Get task by ID."""
        return self.active_tasks.get(task_id)

    def get_active_tasks(self) -> list[AsyncTask]:
        """Get all active (not completed) tasks."""
        return [
            task for task in self.active_tasks.values()
            if task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]
        ]

    def cleanup_completed_tasks(self, max_age_seconds: int = 3600):
        """Remove completed tasks older than max_age."""
        current_time = time.time()
        to_remove = []

        for task_id, task in self.active_tasks.items():
            if task.status in [TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if current_time - task.created_at > max_age_seconds:
                    to_remove.append(task_id)

        for task_id in to_remove:
            del self.active_tasks[task_id]

    async def retry_failed_task(self, task: AsyncTask, poll_func: Callable) -> AsyncTask:
        """Retry a failed task."""
        if task.status != TaskStatus.FAILED:
            return task

        # Reset task
        task.status = TaskStatus.PENDING
        task.error = None
        task.created_at = time.time()

        # Re-poll
        return await self._poll_until_complete(task, poll_func)

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        total = len(self.active_tasks)
        succeeded = sum(1 for t in self.active_tasks.values() if t.status == TaskStatus.SUCCEEDED)
        failed = sum(1 for t in self.active_tasks.values() if t.status == TaskStatus.FAILED)
        processing = sum(1 for t in self.active_tasks.values() if t.status == TaskStatus.PROCESSING)

        return {
            'total_tasks': total,
            'succeeded': succeeded,
            'failed': failed,
            'processing': processing,
            'success_rate': succeeded / total if total > 0 else 0
        }

    def __repr__(self):
        """String representation."""
        stats = self.get_stats()
        return f"<AsyncOrchestrator: {stats['total_tasks']} tasks, {stats['succeeded']} succeeded, {stats['processing']} processing>"
