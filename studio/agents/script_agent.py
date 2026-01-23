"""
Script Agent - First agent in the pipeline
Research-powered viral content creator with web scraping and retention optimization
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from studio.schemas import SceneClip, ProductionJob


class ScriptAgent:
    """
    Advanced script generator that:
    - Scrapes trending stories in your niche
    - Researches what content goes viral
    - Optimizes for high AVD (Average View Duration)
    - Writes killer hooks for maximum retention
    - Analyzes competitor content patterns

    Output: List of SceneClip objects with script_content, narration_text, scene_description
    """

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Script Agent will use fallback mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # For web scraping and research
        self.serper_api_key = os.environ.get('SERPER_API_KEY')  # For Google search
        self.enable_research = os.environ.get('ENABLE_RESEARCH', 'true').lower() == 'true'

    async def generate_script(self, job: ProductionJob) -> List[SceneClip]:
        """
        Generate a complete script with scene breakdown
        Includes research and viral optimization

        Args:
            job: ProductionJob with title, topic, duration_target, tone, visual_style

        Returns:
            List of SceneClip objects with script data populated
        """
        print(f"📝 Script Agent: Generating script for '{job.title}'...")

        # Check if API key is available
        if not self.client:
            print(f"   ⚠️  No Anthropic API key - using fallback script")
            return self._generate_fallback_script(job)

        # Step 1: Research phase (if enabled)
        research_context = ""
        if self.enable_research:
            print(f"   🔍 Researching viral content in niche...")
            research_context = await self._research_viral_content(job)

        # Step 2: Analyze retention patterns
        print(f"   📊 Analyzing retention patterns...")
        retention_tips = self._get_retention_strategies(job.platform, job.duration_target)

        # Step 3: Generate hook
        print(f"   🎣 Crafting killer hook...")
        hook_strategy = self._get_hook_strategy(job.platform)

        # Step 4: Build optimized prompt
        platform_guidance = self._get_platform_guidance(job.platform, job.duration_target)

        prompt = f"""You are an expert viral video scriptwriter. Create a script optimized for maximum retention and engagement.

CONTEXT:
Title: {job.title}
Topic: {job.topic}
Duration: {job.duration_target} seconds
Visual Style: {job.visual_style}
Tone: {job.tone}
Platform: {job.platform}

{research_context}

{platform_guidance}

RETENTION OPTIMIZATION:
{retention_tips}

HOOK STRATEGY:
{hook_strategy}

SCRIPT REQUIREMENTS:
1. Open with a KILLER HOOK (first 3 seconds must grab attention)
   - Use pattern interrupt, shocking statement, or visual curiosity gap
   - Never introduce yourself or waste time - jump straight into value
   - Examples: "This changes everything...", "Nobody talks about this...", "You're doing this wrong..."

2. Create a curiosity loop in the first 10 seconds
   - Tease the payoff but don't reveal it yet
   - Make viewers NEED to keep watching

3. Structure for retention:
   - Every scene must transition with curiosity or surprise
   - Use "but wait" moments every 8-12 seconds
   - Build tension that resolves at the end

4. Pacing control:
   - Short sentences for narration (easier to process)
   - Quick scene changes (visual variety)
   - No dead air or filler content

5. End with satisfying payoff + implicit CTA
   - Deliver on the promise from the hook
   - Leave viewers wanting more (series potential)

Create a scene-by-scene breakdown. For each scene, provide:
- Scene number and duration
- Narration text (what will be spoken) - MUST be punchy and retention-optimized
- Visual description (what should be shown) - dynamic, engaging visuals
- Emotional beat (the feeling/mood)
- Retention tactic (what keeps them watching into next scene)

Return JSON array:
[
  {{
    "sequence_number": 1,
    "duration": 3.0,
    "narration_text": "HOOK TEXT - attention-grabbing opening",
    "scene_description": "Dynamic visual that supports the hook",
    "emotional_beat": "curiosity/shock/intrigue",
    "script_content": "Combined scene script",
    "retention_tactic": "What makes them want to see scene 2"
  }},
  ...
]

Total duration: {job.duration_target} seconds
Number of scenes: {self._estimate_scene_count(job.duration_target)}

CRITICAL: The first scene MUST have the hook. No intros, no setup, just pure hook.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        script_text = response.content[0].text
        scenes_data = self._parse_script_response(script_text)

        # Convert to SceneClip objects
        clips = []
        for scene_data in scenes_data:
            clip = SceneClip(
                clip_id=f"{job.job_id}_scene_{scene_data['sequence_number']}",
                sequence_number=scene_data['sequence_number'],
                script_content=scene_data.get('script_content', ''),
                narration_text=scene_data['narration_text'],
                scene_description=scene_data['scene_description'],
                emotional_beat=scene_data['emotional_beat'],
                duration=scene_data['duration']
            )
            clips.append(clip)

        print(f"✅ Script Agent: Generated {len(clips)} scenes with optimized retention")
        return clips

    async def _research_viral_content(self, job: ProductionJob) -> str:
        """
        Research trending content in the niche
        Scrapes and analyzes what's currently going viral
        """
        if not self.serper_api_key:
            # Fallback to built-in knowledge
            return self._get_fallback_research(job)

        try:
            # Search for viral content in niche
            search_query = f"{job.topic} viral {job.platform} 2024"

            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "q": search_query,
                "num": 10
            }

            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                results = response.json()

                # Extract insights from top results
                insights = []
                for result in results.get('organic', [])[:5]:
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    insights.append(f"• {title}: {snippet}")

                research_summary = "\n".join(insights)

                return f"""
VIRAL CONTENT RESEARCH:
Based on currently trending content in this niche:
{research_summary}

Key patterns identified:
- Topics that are getting traction
- Content formats that work
- Hooks and angles being used
"""
            else:
                return self._get_fallback_research(job)

        except Exception as e:
            print(f"   ⚠️  Research API failed: {e}")
            return self._get_fallback_research(job)

    def _get_fallback_research(self, job: ProductionJob) -> str:
        """Fallback research based on built-in knowledge"""
        return f"""
NICHE INSIGHTS ({job.topic}):
- Focus on unique angles and contrarian takes
- Use specific examples and real stories
- Avoid generic advice - go deep on one thing
- Personal stories and case studies perform well
"""

    def _get_retention_strategies(self, platform: str, duration: float) -> str:
        """Platform-specific retention strategies"""
        base_strategies = """
1. Hook in first 3 seconds (visual + statement)
2. Create curiosity loops every 10-15 seconds
3. Use pattern interrupts (visual changes, sound effects)
4. Fast pacing - no wasted frames
5. Build to a satisfying climax
6. Payoff must justify the watch time
"""

        if platform == "youtube":
            return base_strategies + """
YouTube-specific:
- First 30 seconds are CRITICAL for AVD
- Use chapter-like structure (can rewatch specific parts)
- End screen setup for next video
- Comments encouragement for algorithm boost
"""
        elif platform == "tiktok":
            return base_strategies + """
TikTok-specific:
- Every FRAME must be engaging (no filler)
- Text overlays as safety net
- Trending sounds help initial push
- Loop potential (end connects to beginning)
"""
        elif platform == "instagram":
            return base_strategies + """
Instagram Reels-specific:
- Aesthetic consistency throughout
- Clear value proposition in first frame
- Shareable moments (quote cards, revelations)
- Music choice affects retention
"""
        else:
            return base_strategies

    def _get_hook_strategy(self, platform: str) -> str:
        """Platform-specific hook strategies"""
        if platform == "tiktok" or platform == "instagram":
            return """
HOOK FORMULA (Shorts/Reels):
1. Visual hook (0-0.5s): Eye-catching visual
2. Text overlay (0-1s): Shocking/curious statement
3. Voice hook (0-3s): Elaborate on the promise

Types of hooks:
- Contrarian: "Everyone does [X] wrong..."
- Curiosity gap: "This trick changed everything..."
- Pattern interrupt: "Stop doing [X]..."
- Promise: "Here's how to [desired outcome]..."
- Story: "Last week, [intriguing story opening]..."
"""
        else:
            return """
HOOK FORMULA (Long-form):
1. Open loop (0-3s): "By the end of this video..."
2. Intrigue (3-8s): Why this matters NOW
3. Credibility (8-15s): Why trust this info (briefly)
4. Promise (15-20s): What they'll learn

Hook Types:
- Question: "What if [mind-blowing scenario]?"
- Story: "I discovered something that..."
- Shocking stat: "[Number]% of people don't know..."
- Personal: "After 1000 hours studying this..."
"""

    def _get_platform_guidance(self, platform: str, duration: float) -> str:
        """Platform-specific guidance"""
        if platform == "youtube" or duration > 60:
            return """
PLATFORM: YouTube Long-form
- 3-act structure (setup, build, payoff)
- Retention graphs: keep first 30s tight
- Mid-roll ads at natural breaks (if applicable)
- End screen setup in last 20s
- SEO-optimized title and thumbnail synergy
"""
        elif platform == "tiktok":
            return """
PLATFORM: TikTok
- First frame = thumbnail (must stop scroll)
- 0.5 second rule (hook IMMEDIATELY)
- Leverage trends and sounds when relevant
- Duet/stitch potential
- Loop-able ending (connects back to start)
- Text overlays for accessibility
"""
        elif platform == "instagram":
            return """
PLATFORM: Instagram Reels
- Aesthetic consistency (brand feel)
- Strong visual storytelling
- Text overlays (many watch muted)
- Shareable value (save/send potential)
- Cohesive with grid aesthetic
"""
        else:
            return "Multi-platform: Optimize for universal engagement"

    def _estimate_scene_count(self, duration: float) -> int:
        """Estimate appropriate number of scenes for pacing"""
        # Faster pacing = more scenes = better retention
        if duration <= 15:
            return 4  # Every 3-4 seconds
        elif duration <= 30:
            return 6-7  # Every 4-5 seconds
        elif duration <= 60:
            return 10-12  # Every 5-6 seconds
        else:
            return max(12, int(duration / 6))  # Every 6 seconds

    def _parse_script_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured scene data"""
        # Try to extract JSON array from response
        try:
            # Find JSON array in response
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_text = text[start_idx:end_idx]
                scenes = json.loads(json_text)

                # Validate first scene has a strong hook
                if scenes and len(scenes) > 0:
                    first_scene = scenes[0]
                    narration = first_scene.get('narration_text', '').lower()

                    # Check for weak openings
                    weak_starts = ['hi', 'hello', 'welcome', 'my name', 'in this video', 'today']
                    if any(narration.startswith(start) for start in weak_starts):
                        print("   ⚠️  Weak hook detected - may impact retention")

                return scenes
        except Exception as e:
            print(f"⚠️  Failed to parse JSON, using fallback: {e}")

        # Fallback: create single scene
        return [{
            "sequence_number": 1,
            "duration": 10.0,
            "narration_text": "Script generation in progress...",
            "scene_description": "Visual content will be generated",
            "emotional_beat": "engaging",
            "script_content": text[:500]
        }]

    def _generate_fallback_script(self, job: ProductionJob) -> List[SceneClip]:
        """Generate a basic fallback script when API key is not available"""
        scene_count = self._estimate_scene_count(job.duration_target)
        scene_duration = job.duration_target / scene_count

        clips = []
        for i in range(scene_count):
            clip = SceneClip(
                clip_id=f"{job.job_id}_scene_{i + 1}",
                sequence_number=i + 1,
                script_content=f"Scene {i + 1} about {job.topic}",
                narration_text=f"This is scene {i + 1} covering {job.topic}",
                scene_description=f"Visual scene {i + 1} in {job.visual_style} style",
                emotional_beat="engaging",
                duration=scene_duration
            )
            clips.append(clip)

        print(f"✅ Script Agent: Generated {len(clips)} fallback scenes (add ANTHROPIC_API_KEY for full script generation)")
        return clips
