"""
Thumbnail Agent - CTR-optimized thumbnail generator
Uses Nano Banana Pro and analytics insights to create click-worthy thumbnails
"""
import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from studio.schemas import ProductionJob
from studio.providers.kieai_provider import KieAIProvider


class ThumbnailVariant:
    """Represents a thumbnail design variant"""
    def __init__(
        self,
        variant_id: str,
        image_url: str,
        design_strategy: str,
        text_overlay: str,
        color_scheme: str,
        composition: str,
        predicted_ctr: float,  # Estimated CTR based on analytics
        description: str
    ):
        self.variant_id = variant_id
        self.image_url = image_url
        self.design_strategy = design_strategy
        self.text_overlay = text_overlay
        self.color_scheme = color_scheme
        self.composition = composition
        self.predicted_ctr = predicted_ctr
        self.description = description

    def to_dict(self):
        return {
            "variant_id": self.variant_id,
            "image_url": self.image_url,
            "design_strategy": self.design_strategy,
            "text_overlay": self.text_overlay,
            "color_scheme": self.color_scheme,
            "composition": self.composition,
            "predicted_ctr": self.predicted_ctr,
            "description": self.description
        }


class ThumbnailAgent:
    """
    Expert thumbnail designer that:
    - Generates eye-catching thumbnails with Nano Banana Pro
    - Uses analytics insights to optimize for CTR
    - Creates multiple A/B test variants
    - Follows platform-specific best practices
    - Applies proven CTR-boosting techniques:
      * High contrast and saturation
      * Faces with exaggerated expressions
      * Text overlays with bold fonts
      * Curiosity gaps and pattern interrupts
      * Bright colors that stand out in feed
    - Learns from channel's best-performing thumbnails
    """

    def __init__(self):
        # LLM for thumbnail strategy
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Thumbnail Agent will use basic mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # Nano Banana Pro for image generation
        kieai_api_key = os.environ.get('KIEAI_API_KEY')
        self.use_mock = os.environ.get('STUDIO_MOCK_GENERATION', 'false').lower() == 'true'

        if kieai_api_key and not self.use_mock:
            self.kieai_provider = KieAIProvider(api_key=kieai_api_key)
        else:
            self.kieai_provider = None

        # Load analytics insights
        self.analytics_insights = self._load_analytics_insights()

    async def generate_thumbnails(
        self,
        job: ProductionJob,
        num_variants: int = 3
    ) -> List[ThumbnailVariant]:
        """
        Main method: Generate thumbnail variants optimized for CTR

        Args:
            job: ProductionJob with video info
            num_variants: Number of thumbnail variants to create

        Returns:
            List of ThumbnailVariant objects
        """
        print(f"🖼️  Thumbnail Agent: Generating {num_variants} thumbnail variants for '{job.title}'...")

        # Step 1: Analyze what makes thumbnails click-worthy
        print(f"   🎯 Analyzing CTR optimization strategies...")
        design_strategies = await self._plan_thumbnail_strategies(job, num_variants)

        # Step 2: Generate each variant
        thumbnails = []
        for i, strategy in enumerate(design_strategies):
            print(f"   🎨 Generating variant {i+1}/{num_variants}: {strategy['design_strategy']}...")

            variant = await self._generate_single_thumbnail(
                job,
                strategy,
                variant_number=i+1
            )

            if variant:
                thumbnails.append(variant)

        # Step 3: Rank by predicted CTR
        thumbnails.sort(key=lambda t: t.predicted_ctr, reverse=True)

        print(f"✅ Thumbnail Agent: Generated {len(thumbnails)} thumbnails (best predicted CTR: {thumbnails[0].predicted_ctr:.1%})")

        return thumbnails

    async def _plan_thumbnail_strategies(
        self,
        job: ProductionJob,
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """
        Plan different thumbnail design strategies to test
        """
        if not self.client:
            return self._get_default_strategies(job, num_variants)

        try:
            # Load analytics insights about successful thumbnails
            thumbnail_insights = self._get_thumbnail_insights()

            prompt = f"""You are a YouTube thumbnail expert. Plan {num_variants} different thumbnail design strategies for this video.

VIDEO INFO:
Title: {job.title}
Topic: {job.topic}
Platform: {job.platform}
Tone: {job.tone}

ANALYTICS INSIGHTS:
{thumbnail_insights}

For each thumbnail variant, provide:
1. Design strategy (e.g., "bold text + shocked face", "before/after split", "mystery reveal")
2. Visual description for image generation
3. Text overlay (3-5 words max, BIG and readable)
4. Color scheme (high contrast, vibrant)
5. Composition (rule of thirds, close-up, etc.)
6. Why this will get clicks (psychological trigger)
7. Predicted CTR score (0-100)

CTR-BOOSTING TECHNIQUES TO USE:
- High contrast colors (yellow/black, red/white, blue/orange)
- Faces with exaggerated expressions (shock, excitement, confusion)
- Arrows and circles to draw attention
- Numbers and stats (if applicable)
- Before/after comparisons
- Curiosity gaps ("You won't believe...")
- Pattern interrupts (unexpected elements)
- Text that's readable even at small size

Return JSON array:
[
  {{
    "design_strategy": "bold strategy name",
    "visual_description": "detailed prompt for image generation",
    "text_overlay": "BIG TEXT",
    "color_scheme": "yellow and black",
    "composition": "close-up face with shocked expression",
    "click_trigger": "shock and curiosity",
    "predicted_ctr": 8.5
  }},
  ...
]"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text

            # Extract JSON
            start_idx = analysis_text.find('[')
            end_idx = analysis_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                strategies = json.loads(analysis_text[start_idx:end_idx])
                return strategies[:num_variants]

        except Exception as e:
            print(f"   ⚠️  Strategy planning failed: {e}")

        return self._get_default_strategies(job, num_variants)

    async def _generate_single_thumbnail(
        self,
        job: ProductionJob,
        strategy: Dict[str, Any],
        variant_number: int
    ) -> Optional[ThumbnailVariant]:
        """
        Generate a single thumbnail using Nano Banana Pro
        """
        visual_description = strategy.get('visual_description', '')
        text_overlay = strategy.get('text_overlay', '')
        color_scheme = strategy.get('color_scheme', 'vibrant')

        # Build optimized prompt for Nano Banana Pro
        thumbnail_prompt = f"""YouTube thumbnail image, professional design, high quality:

{visual_description}

Style: {color_scheme}, high contrast, eye-catching, vibrant colors, bold composition
Text on image: "{text_overlay}" in large bold font
Quality: 4K, sharp, professional thumbnail design
Lighting: dramatic, high contrast
Mood: attention-grabbing, click-worthy

Professional YouTube thumbnail, perfect composition, optimized for small screen viewing"""

        # Platform-specific dimensions
        if job.platform == "youtube":
            width, height = 1280, 720  # 16:9
        elif job.platform == "tiktok":
            width, height = 1080, 1920  # 9:16
        elif job.platform == "instagram":
            width, height = 1080, 1080  # 1:1
        else:
            width, height = 1280, 720

        # Generate with Nano Banana Pro
        if self.kieai_provider and not self.use_mock:
            try:
                image_data = self.kieai_provider.generate_image_nano_banana_pro(
                    prompt=thumbnail_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=30,  # Higher quality for thumbnails
                    guidance_scale=8.5
                )

                image_url = image_data.get('image_url')

                print(f"   ✅ Variant {variant_number} generated")

                return ThumbnailVariant(
                    variant_id=f"{job.job_id}_thumb_v{variant_number}",
                    image_url=image_url,
                    design_strategy=strategy.get('design_strategy', ''),
                    text_overlay=text_overlay,
                    color_scheme=color_scheme,
                    composition=strategy.get('composition', ''),
                    predicted_ctr=strategy.get('predicted_ctr', 5.0) / 100.0,
                    description=strategy.get('click_trigger', '')
                )

            except Exception as e:
                print(f"   ⚠️  Thumbnail generation failed: {e}")

        # Mock mode or fallback
        return ThumbnailVariant(
            variant_id=f"{job.job_id}_thumb_v{variant_number}",
            image_url=f"https://example.com/thumbnails/mock_v{variant_number}.jpg",
            design_strategy=strategy.get('design_strategy', 'default'),
            text_overlay=text_overlay,
            color_scheme=color_scheme,
            composition=strategy.get('composition', 'standard'),
            predicted_ctr=strategy.get('predicted_ctr', 5.0) / 100.0,
            description=f"[MOCK] {strategy.get('click_trigger', 'engaging thumbnail')}"
        )

    def _get_thumbnail_insights(self) -> str:
        """
        Get insights from analytics about what thumbnails work
        """
        if not self.analytics_insights:
            return "No analytics insights available yet. Using proven thumbnail best practices."

        # Extract thumbnail-specific insights
        thumbnail_insights = [
            insight for insight in self.analytics_insights
            if insight.get('insight_type') == 'thumbnail'
        ]

        if len(thumbnail_insights) == 0:
            return "No thumbnail insights available yet. Using proven thumbnail best practices."

        insights_text = "\n".join([
            f"- {insight.get('finding', '')} (confidence: {insight.get('confidence', 0):.0%})"
            for insight in thumbnail_insights
        ])

        return f"Thumbnail insights from your channel:\n{insights_text}"

    def _load_analytics_insights(self) -> List[Dict]:
        """Load analytics insights from database"""
        try:
            insights_path = "data/analytics_insights.json"
            if os.path.exists(insights_path):
                with open(insights_path, 'r') as f:
                    data = json.load(f)
                    return data.get('insights', [])
        except Exception as e:
            print(f"   ⚠️  Could not load analytics insights: {e}")

        return []

    def _get_default_strategies(
        self,
        job: ProductionJob,
        num_variants: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback thumbnail strategies when LLM not available
        """
        base_strategies = [
            {
                "design_strategy": "Bold text + vibrant colors",
                "visual_description": f"Eye-catching image about {job.topic}, vibrant colors, professional composition",
                "text_overlay": job.title[:20].upper(),
                "color_scheme": "yellow and black",
                "composition": "centered, bold",
                "click_trigger": "high contrast and readability",
                "predicted_ctr": 6.5
            },
            {
                "design_strategy": "Curiosity-driven visual",
                "visual_description": f"Mysterious and intriguing visual about {job.topic}, dramatic lighting",
                "text_overlay": "WATCH THIS",
                "color_scheme": "red and white",
                "composition": "close-up with arrows",
                "click_trigger": "curiosity and urgency",
                "predicted_ctr": 7.2
            },
            {
                "design_strategy": "High-energy dynamic",
                "visual_description": f"Dynamic action shot related to {job.topic}, energetic composition",
                "text_overlay": "AMAZING",
                "color_scheme": "blue and orange",
                "composition": "diagonal movement",
                "click_trigger": "excitement and movement",
                "predicted_ctr": 6.8
            }
        ]

        return base_strategies[:num_variants]

    async def analyze_thumbnail_performance(
        self,
        thumbnail_id: str,
        actual_ctr: float,
        views: int
    ):
        """
        Learn from thumbnail performance to improve future generations
        This is called after a video is posted and gets initial metrics
        """
        print(f"📊 Thumbnail Agent: Learning from thumbnail {thumbnail_id} (CTR: {actual_ctr:.2%})...")

        # Save performance data
        try:
            perf_path = "data/thumbnail_performance.json"

            perf_data = []
            if os.path.exists(perf_path):
                with open(perf_path, 'r') as f:
                    perf_data = json.load(f).get('thumbnails', [])

            perf_data.append({
                "thumbnail_id": thumbnail_id,
                "actual_ctr": actual_ctr,
                "views": views,
                "analyzed_at": "now"
            })

            with open(perf_path, 'w') as f:
                json.dump({"thumbnails": perf_data}, f, indent=2)

            print(f"   💾 Saved performance data for future learning")

        except Exception as e:
            print(f"   ⚠️  Could not save performance data: {e}")
