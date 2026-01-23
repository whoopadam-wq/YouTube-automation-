"""
Cost Estimator - Production cost calculator and budget planner
Calculates costs for different video lengths and provides breakdowns
"""
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a production"""
    video_duration: float  # in minutes
    total_cost: float
    script_generation: float
    image_generation: float
    video_generation: float
    audio_synthesis: float
    motion_graphics: float
    thumbnail_generation: float
    api_overhead: float
    breakdown_details: Dict[str, Any]

    def to_dict(self):
        return {
            "video_duration_minutes": self.video_duration,
            "total_cost_usd": round(self.total_cost, 2),
            "breakdown": {
                "script_generation": round(self.script_generation, 2),
                "image_generation": round(self.image_generation, 2),
                "video_generation": round(self.video_generation, 2),
                "audio_synthesis": round(self.audio_synthesis, 2),
                "motion_graphics": round(self.motion_graphics, 2),
                "thumbnail_generation": round(self.thumbnail_generation, 2),
                "api_overhead": round(self.api_overhead, 2)
            },
            "details": self.breakdown_details
        }


class CostEstimator:
    """
    Production cost calculator that:
    - Knows pricing for all AI tools and services
    - Calculates costs for different video durations
    - Provides detailed breakdowns by component
    - Estimates before production starts
    - Tracks actual costs vs estimates
    - Helps users budget their content
    - Updates with latest pricing info
    """

    def __init__(self):
        # Tool pricing (USD) - researched and maintained
        self.pricing = self._load_pricing_data()

        # Usage patterns (average)
        self.usage_patterns = {
            "scenes_per_minute": 12,  # Average 5 seconds per scene
            "llm_calls_per_video": 8,  # Script + Character + Lighting + Composition + Frame + Analytics
            "images_per_scene": 2,  # Start and end frame
            "motion_graphics_per_minute": 2,  # Average motion graphics density
            "thumbnail_variants": 3
        }

    def estimate_production_cost(
        self,
        duration_minutes: float,
        platform: str = "youtube",
        include_motion_graphics: bool = True,
        quality_tier: str = "standard"  # "economy", "standard", "premium"
    ) -> CostBreakdown:
        """
        Main method: Estimate production cost for a video

        Args:
            duration_minutes: Video length in minutes (e.g., 8, 15, 20, 40)
            platform: Target platform (affects dimensions/processing)
            include_motion_graphics: Whether to include Remotion graphics
            quality_tier: Quality level affects tool selection and iterations

        Returns:
            CostBreakdown with detailed cost analysis
        """
        print(f"💰 Cost Estimator: Calculating cost for {duration_minutes}-minute {platform} video...")

        duration_seconds = duration_minutes * 60
        num_scenes = int(duration_minutes * self.usage_patterns["scenes_per_minute"])

        # Component costs
        script_cost = self._estimate_script_cost(duration_minutes, quality_tier)
        image_cost = self._estimate_image_cost(num_scenes, quality_tier)
        video_cost = self._estimate_video_cost(num_scenes, duration_seconds, quality_tier)
        audio_cost = self._estimate_audio_cost(duration_seconds, quality_tier)
        motion_cost = self._estimate_motion_graphics_cost(duration_minutes) if include_motion_graphics else 0
        thumbnail_cost = self._estimate_thumbnail_cost(quality_tier)
        overhead_cost = self._estimate_api_overhead(duration_minutes)

        total_cost = (
            script_cost +
            image_cost +
            video_cost +
            audio_cost +
            motion_cost +
            thumbnail_cost +
            overhead_cost
        )

        details = {
            "num_scenes": num_scenes,
            "num_images": num_scenes * 2,
            "num_video_clips": num_scenes,
            "audio_duration_seconds": duration_seconds,
            "num_llm_calls": self.usage_patterns["llm_calls_per_video"],
            "num_thumbnails": self.usage_patterns["thumbnail_variants"],
            "motion_graphics_elements": int(duration_minutes * self.usage_patterns["motion_graphics_per_minute"]) if include_motion_graphics else 0,
            "quality_tier": quality_tier,
            "platform": platform
        }

        print(f"✅ Cost Estimator: ${total_cost:.2f} for {duration_minutes}-minute video")

        return CostBreakdown(
            video_duration=duration_minutes,
            total_cost=total_cost,
            script_generation=script_cost,
            image_generation=image_cost,
            video_generation=video_cost,
            audio_synthesis=audio_cost,
            motion_graphics=motion_cost,
            thumbnail_generation=thumbnail_cost,
            api_overhead=overhead_cost,
            breakdown_details=details
        )

    def compare_durations(
        self,
        durations: List[float] = [8, 15, 20, 40]
    ) -> Dict[str, Any]:
        """
        Compare costs for different video durations
        Useful for budget planning

        Returns:
            Dict with estimates for each duration
        """
        print(f"📊 Cost Estimator: Comparing costs for {len(durations)} durations...")

        comparisons = {}

        for duration in durations:
            estimate = self.estimate_production_cost(duration)
            comparisons[f"{int(duration)}min"] = estimate.to_dict()

        # Calculate cost per minute for each
        for duration_key, estimate in comparisons.items():
            duration_val = estimate["video_duration_minutes"]
            cost_per_minute = estimate["total_cost_usd"] / duration_val
            estimate["cost_per_minute"] = round(cost_per_minute, 2)

        print(f"✅ Cost Estimator: Comparison complete")

        return {
            "comparisons": comparisons,
            "best_value": self._find_best_value(comparisons),
            "generated_at": "now"
        }

    def _estimate_script_cost(
        self,
        duration_minutes: float,
        quality_tier: str
    ) -> float:
        """
        Estimate cost of script generation
        Uses Claude 3.5 Sonnet via Anthropic API
        """
        # Script generation complexity scales with duration
        # More scenes = more detailed script = more tokens

        num_scenes = int(duration_minutes * self.usage_patterns["scenes_per_minute"])

        # Anthropic pricing: ~$3 per million input tokens, $15 per million output tokens
        # Estimate: 1000 input tokens (prompt) + 300 output tokens per scene

        input_tokens = 1000 + (num_scenes * 200)  # Prompt + scene descriptions
        output_tokens = num_scenes * 300  # Detailed scene script

        input_cost = (input_tokens / 1_000_000) * self.pricing["anthropic"]["claude_3_5_sonnet"]["input"]
        output_cost = (output_tokens / 1_000_000) * self.pricing["anthropic"]["claude_3_5_sonnet"]["output"]

        # Also includes character lock, lighting, composition, frame agents
        total_llm_calls = self.usage_patterns["llm_calls_per_video"]

        return (input_cost + output_cost) * total_llm_calls

    def _estimate_image_cost(
        self,
        num_scenes: int,
        quality_tier: str
    ) -> float:
        """
        Estimate cost of image generation
        Uses Nano Banana Pro via kie.ai
        """
        # 2 images per scene (start and end frame)
        num_images = num_scenes * 2

        # Nano Banana Pro pricing via kie.ai
        cost_per_image = self.pricing["kieai"]["nano_banana_pro"]["per_image"]

        return num_images * cost_per_image

    def _estimate_video_cost(
        self,
        num_scenes: int,
        total_duration_seconds: float,
        quality_tier: str
    ) -> float:
        """
        Estimate cost of video generation
        Uses Veo 3 via kie.ai

        Veo 3 charges per video scene generated (typically 5-second clips)
        NOT per second of final video
        """
        # Get cost per scene generation
        cost_per_scene = self.pricing["kieai"]["veo_3"]["per_scene"]

        # Total cost is number of scenes × cost per scene
        return num_scenes * cost_per_scene

    def _estimate_audio_cost(
        self,
        duration_seconds: float,
        quality_tier: str
    ) -> float:
        """
        Estimate cost of audio generation
        Uses ElevenLabs via kie.ai
        """
        # ElevenLabs charges per character
        # Average speaking rate: ~150 words per minute = ~900 characters per minute
        duration_minutes = duration_seconds / 60
        estimated_characters = int(duration_minutes * 900)

        cost_per_character = self.pricing["kieai"]["elevenlabs"]["per_character"]

        return estimated_characters * cost_per_character

    def _estimate_motion_graphics_cost(
        self,
        duration_minutes: float
    ) -> float:
        """
        Estimate cost of motion graphics
        Remotion rendering + LLM code generation
        """
        # Motion graphics cost = LLM code generation + rendering compute

        num_elements = int(duration_minutes * self.usage_patterns["motion_graphics_per_minute"])

        # Code generation (Claude)
        tokens_per_element = 2000  # Generate Remotion code
        code_gen_cost = (num_elements * tokens_per_element / 1_000_000) * self.pricing["anthropic"]["claude_3_5_sonnet"]["output"]

        # Rendering cost (estimated)
        render_cost_per_minute = 0.10  # Approximate compute cost
        render_cost = duration_minutes * render_cost_per_minute

        return code_gen_cost + render_cost

    def _estimate_thumbnail_cost(
        self,
        quality_tier: str
    ) -> float:
        """
        Estimate cost of thumbnail generation
        Generates 3 variants using Nano Banana Pro
        """
        num_variants = self.usage_patterns["thumbnail_variants"]
        cost_per_image = self.pricing["kieai"]["nano_banana_pro"]["per_image"]

        return num_variants * cost_per_image

    def _estimate_api_overhead(
        self,
        duration_minutes: float
    ) -> float:
        """
        Estimate API overhead costs
        Analytics, ideas scraper, etc.
        """
        # Small additional costs for:
        # - Ideas scraper (Serper API)
        # - Analytics (YouTube Data API)
        # - Miscellaneous API calls

        base_overhead = 0.05  # $0.05 base
        per_minute_overhead = 0.02

        return base_overhead + (duration_minutes * per_minute_overhead)

    def _find_best_value(
        self,
        comparisons: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Find the best value (lowest cost per minute)
        """
        best_key = None
        best_cpm = float('inf')

        for key, data in comparisons.items():
            cpm = data.get('cost_per_minute', float('inf'))
            if cpm < best_cpm:
                best_cpm = cpm
                best_key = key

        return {
            "duration": best_key,
            "cost_per_minute": best_cpm,
            "reason": "Lowest cost per minute of content"
        }

    def _load_pricing_data(self) -> Dict[str, Any]:
        """
        Load current pricing data for all services
        Researched and maintained pricing information
        """
        return {
            "anthropic": {
                "claude_3_5_sonnet": {
                    "input": 3.0,  # per million tokens
                    "output": 15.0
                },
                "claude_3_opus": {
                    "input": 15.0,
                    "output": 75.0
                }
            },
            "kieai": {
                "nano_banana_pro": {
                    "per_image": 0.02  # Kie.ai pricing
                },
                "veo_3": {
                    "per_scene": 0.08  # Per video scene generated (5-second clips)
                },
                "elevenlabs": {
                    "per_character": 0.0003  # Kie.ai pricing
                },
                "musicgen": {
                    "per_generation": 0.05  # Kie.ai pricing
                }
            },
            "serper": {
                "per_search": 0.001  # $1 per 1000 searches
            },
            "youtube": {
                "data_api": 0.0,  # Free tier generous
                "analytics_api": 0.0
            }
        }

    def save_pricing_update(self, new_pricing: Dict[str, Any]):
        """
        Update pricing data (for when prices change)
        Saves to file for persistence
        """
        pricing_file = "data/pricing_data.json"

        try:
            with open(pricing_file, 'w') as f:
                json.dump(new_pricing, f, indent=2)

            self.pricing = new_pricing
            print(f"✅ Pricing data updated and saved")

        except Exception as e:
            print(f"⚠️  Could not save pricing update: {e}")

    def generate_pricing_report(self) -> str:
        """
        Generate human-readable pricing report
        """
        report = """
# AI Video Production - Cost Breakdown

## Standard Video Durations

### 8-Minute Video
{8min}

### 15-Minute Video
{15min}

### 20-Minute Video
{20min}

### 40-Minute Video
{40min}

## Pricing Notes
- Costs include all AI services (LLM, image, video, audio generation)
- Motion graphics add ~$0.20-0.30 per minute
- Longer videos have better cost-per-minute efficiency
- Prices subject to change based on provider updates

## Cost Optimization Tips
1. **Batch production**: Produce multiple videos together
2. **Optimize duration**: 15-20 minutes has best value
3. **Reduce variants**: Fewer thumbnail variants saves cost
4. **Quality tiers**: Use standard quality for most content

Generated: {date}
"""

        estimates = self.compare_durations([8, 15, 20, 40])

        return report.format(
            **{f"{int(k.replace('min', ''))}min": self._format_estimate(v) for k, v in estimates["comparisons"].items()},
            date="now"
        )

    def _format_estimate(self, estimate: Dict) -> str:
        """Format estimate for report"""
        return f"""
Total Cost: ${estimate['total_cost_usd']:.2f}
Cost per Minute: ${estimate['cost_per_minute']:.2f}

Breakdown:
- Script Generation: ${estimate['breakdown']['script_generation']:.2f}
- Image Generation: ${estimate['breakdown']['image_generation']:.2f}
- Video Generation: ${estimate['breakdown']['video_generation']:.2f}
- Audio Synthesis: ${estimate['breakdown']['audio_synthesis']:.2f}
- Motion Graphics: ${estimate['breakdown']['motion_graphics']:.2f}
- Thumbnails: ${estimate['breakdown']['thumbnail_generation']:.2f}
"""


# Convenience function for quick estimates
def quick_estimate(duration_minutes: float) -> Dict[str, Any]:
    """Quick cost estimate for a video duration"""
    estimator = CostEstimator()
    breakdown = estimator.estimate_production_cost(duration_minutes)
    return breakdown.to_dict()


# Convenience function for comparing durations
def compare_video_durations() -> Dict[str, Any]:
    """Compare costs for standard video durations"""
    estimator = CostEstimator()
    return estimator.compare_durations([8, 15, 20, 40])
