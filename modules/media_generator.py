"""
Media Generator Module
Generates images and videos for scenes using async API orchestration.
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import aiohttp
import tempfile


class MediaGenerator:
    """
    Generates images and videos for scenes.
    Uses AsyncOrchestrator for efficient parallel generation.
    """

    def __init__(self, config_manager, cost_tracker, async_orchestrator):
        """Initialize media generator."""
        self.config = config_manager
        self.cost_tracker = cost_tracker
        self.orchestrator = async_orchestrator
        self.asset_dir = config_manager.data_path / "assets"
        self.asset_dir.mkdir(parents=True, exist_ok=True)

    async def generate_scene_media(
        self,
        scene_plans: List[Dict],
        channel_config: Dict[str, Any],
        video_id: str
    ) -> List[Dict[str, str]]:
        """
        Generate all media for scenes in parallel.

        Args:
            scene_plans: List of ScenePlan objects
            channel_config: Channel configuration
            video_id: Video ID for organization

        Returns:
            List of dicts with scene_id, image_url, video_url
        """
        # Step 1: Generate all start frame images in parallel
        image_tasks = []
        for scene_plan in scene_plans:
            task_config = {
                'submit_func': lambda sp=scene_plan: self._submit_image_generation(sp, channel_config),
                'poll_func': lambda tid: self._poll_image_status(tid),
                'provider': self._get_image_provider(),
                'task_type': 'image_generation',
                'metadata': {'scene_id': scene_plan['scene_id'], 'video_id': video_id}
            }
            image_tasks.append(task_config)

        print(f"Generating {len(image_tasks)} images in parallel...")
        image_results = await self.orchestrator.submit_batch(image_tasks)

        # Step 2: Generate videos from images in parallel
        video_tasks = []
        for i, scene_plan in enumerate(scene_plans):
            if i < len(image_results) and image_results[i].result_url:
                task_config = {
                    'submit_func': lambda img=image_results[i].result_url, sp=scene_plan:
                        self._submit_video_generation(img, sp, channel_config),
                    'poll_func': lambda tid: self._poll_video_status(tid),
                    'provider': self._get_video_provider(),
                    'task_type': 'video_generation',
                    'metadata': {'scene_id': scene_plan['scene_id'], 'video_id': video_id}
                }
                video_tasks.append(task_config)

        print(f"Generating {len(video_tasks)} videos in parallel...")
        video_results = await self.orchestrator.submit_batch(video_tasks)

        # Step 3: Combine results
        media_assets = []
        for i, scene_plan in enumerate(scene_plans):
            asset = {
                'scene_id': scene_plan['scene_id'],
                'image_url': image_results[i].result_url if i < len(image_results) else None,
                'video_url': video_results[i].result_url if i < len(video_results) else None,
            }
            media_assets.append(asset)

            # Track costs
            if asset['image_url']:
                self.cost_tracker.record_cost(
                    channel_id=channel_config['channel_id'],
                    category='image_generation',
                    provider=self._get_image_provider(),
                    amount=0.10,
                    video_id=video_id
                )

            if asset['video_url']:
                self.cost_tracker.record_cost(
                    channel_id=channel_config['channel_id'],
                    category='video_generation',
                    provider=self._get_video_provider(),
                    amount=2.00,
                    video_id=video_id
                )

        return media_assets

    async def _submit_image_generation(
        self,
        scene_plan: Dict,
        channel_config: Dict
    ) -> str:
        """Submit image generation task."""
        from api_providers import ReplicateProvider, OpenAIProvider

        provider_name = self._get_image_provider()
        provider_config = self.config.get_provider_config('image_generation')
        api_key = self.config.get_api_key(provider_name)

        # Build enhanced prompt
        prompt = self._build_image_prompt(scene_plan, channel_config)

        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
            # For replicate, we need to use async pattern
            task_id = await provider.submit_async(
                model=provider_config['models']['replicate'],
                input_params={
                    'prompt': prompt,
                    'width': 1920,
                    'height': 1080
                }
            )
            return task_id
        else:
            # OpenAI is synchronous, wrap it
            provider = OpenAIProvider(api_key, provider_config)
            url = await provider.generate_image(prompt=prompt)
            return url

    async def _submit_video_generation(
        self,
        image_url: str,
        scene_plan: Dict,
        channel_config: Dict
    ) -> str:
        """Submit video generation task."""
        from api_providers import ReplicateProvider

        provider_name = self._get_video_provider()
        provider_config = self.config.get_provider_config('video_generation')
        api_key = self.config.get_api_key(provider_name)

        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
            task_id = await provider.submit_async(
                model=provider_config['models']['replicate'],
                input_params={
                    'input_image': image_url,
                    'motion_bucket_id': 127
                }
            )
            return task_id

        # Fallback: return image as video
        return image_url

    async def _poll_image_status(self, task_id: str) -> Dict:
        """Poll image generation status."""
        from api_providers import ReplicateProvider

        provider_name = self._get_image_provider()
        provider_config = self.config.get_provider_config('image_generation')
        api_key = self.config.get_api_key(provider_name)

        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
            return await provider.poll_status(task_id)

        return {'status': 'succeeded', 'output': task_id}

    async def _poll_video_status(self, task_id: str) -> Dict:
        """Poll video generation status."""
        from api_providers import ReplicateProvider

        provider_name = self._get_video_provider()
        provider_config = self.config.get_provider_config('video_generation')
        api_key = self.config.get_api_key(provider_name)

        if provider_name == 'replicate':
            provider = ReplicateProvider(api_key, provider_config)
            return await provider.poll_status(task_id)

        return {'status': 'succeeded', 'output': task_id}

    def _build_image_prompt(
        self,
        scene_plan: Dict,
        channel_config: Dict
    ) -> str:
        """Build optimized image generation prompt."""
        style = channel_config['visual_style']

        style_suffixes = {
            'gritty': 'dark moody atmosphere, film noir lighting, high contrast, dramatic shadows',
            'clean': 'bright clean lighting, minimalist, modern aesthetic, soft shadows',
            'dramatic': 'cinematic lighting, epic composition, dramatic atmosphere',
            'minimal': 'simple composition, clean background, focused subject',
            'vibrant': 'vibrant colors, energetic, saturated, high contrast'
        }

        prompt = f"""{scene_plan['start_frame_prompt']}.

{scene_plan['environment_description']}.
{scene_plan['lighting_design']}.
Camera: {scene_plan['camera_distance']} shot.

Style: {style_suffixes.get(style, 'cinematic')}.

Professional quality, detailed, high resolution.
"""
        return prompt.strip()

    def _get_image_provider(self) -> str:
        """Get configured image provider."""
        provider_config = self.config.get_provider_config('image_generation')
        return provider_config.get('primary', 'replicate')

    def _get_video_provider(self) -> str:
        """Get configured video provider."""
        provider_config = self.config.get_provider_config('video_generation')
        return provider_config.get('primary', 'replicate')

    async def download_asset(self, url: str, filename: str) -> str:
        """Download asset from URL to local storage."""
        output_path = self.asset_dir / filename

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    return str(output_path)

        return url  # Return original URL if download fails
