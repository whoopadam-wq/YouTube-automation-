"""
Autonomous Learning System - Continuous improvement and trend monitoring
Self-learning brain that makes the system smarter over time
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
from studio.agents.ideas_scraper_agent import IdeasScraperAgent
from studio.agents.analytics_agent import AnalyticsAgent
from studio.channel_integration import YouTubeChannelIntegration


class LearningInsight:
    """Represents a learning/improvement discovered by the system"""
    def __init__(
        self,
        insight_type: str,  # "performance", "trend", "technique", "pattern"
        category: str,  # "hooks", "thumbnails", "topics", "retention", "timing"
        finding: str,
        confidence: float,
        impact_score: float,  # 1-10
        action_items: List[str],
        data_points: int,
        discovered_at: str
    ):
        self.insight_type = insight_type
        self.category = category
        self.finding = finding
        self.confidence = confidence
        self.impact_score = impact_score
        self.action_items = action_items
        self.data_points = data_points
        self.discovered_at = discovered_at

    def to_dict(self):
        return {
            "insight_type": self.insight_type,
            "category": self.category,
            "finding": self.finding,
            "confidence": self.confidence,
            "impact_score": self.impact_score,
            "action_items": self.action_items,
            "data_points": self.data_points,
            "discovered_at": self.discovered_at
        }


class AutonomousLearningSystem:
    """
    Continuously running self-learning system that:
    - Monitors channel performance 24/7
    - Discovers trends in real-time
    - Analyzes what works and what doesn't
    - Updates agent strategies automatically
    - Tracks viral opportunities
    - Improves recommendations over time
    - Learns from successful videos
    - Adapts to algorithm changes
    - Constantly getting smarter
    - Never stops learning

    This is the "brain" that makes the entire system improve autonomously.
    """

    def __init__(self, channel_id: Optional[str] = None):
        # LLM for analysis
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Learning System will use basic mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # Channel context
        self.channel_id = channel_id
        self.channel_integration = YouTubeChannelIntegration()

        # Agents
        self.analytics_agent = None
        self.ideas_agent = None

        # Learning database
        self.learnings_db_path = "data/autonomous_learnings.json"
        self.trends_db_path = "data/trend_monitor.json"

        # State tracking
        self.is_running = False
        self.last_analysis_time = None
        self.learning_iteration = 0

        # Configuration
        self.monitor_interval_hours = 6  # Check every 6 hours
        self.trend_check_interval_hours = 2  # Check trends more frequently

        # Ensure data directory
        os.makedirs("data", exist_ok=True)

    async def start_continuous_learning(
        self,
        initial_delay_seconds: int = 0
    ):
        """
        Main method: Start the continuous learning loop
        Runs indefinitely, constantly improving

        Args:
            initial_delay_seconds: Delay before starting (for scheduling)
        """
        print(f"🧠 Autonomous Learning: Starting continuous learning system...")

        if initial_delay_seconds > 0:
            print(f"   ⏱️  Waiting {initial_delay_seconds}s before starting...")
            await asyncio.sleep(initial_delay_seconds)

        self.is_running = True

        # Load active channel if not set
        if not self.channel_id:
            active_channel = self.channel_integration.load_active_channel()
            if active_channel:
                self.channel_id = active_channel.channel_id
                print(f"   📺 Loaded active channel: {active_channel.channel_name}")

        if not self.channel_id:
            print(f"   ⚠️  No channel set - learning system will wait for channel integration")

        # Initialize agents
        if self.channel_id:
            self.analytics_agent = AnalyticsAgent(channel_id=self.channel_id)
            self.ideas_agent = IdeasScraperAgent(channel_id=self.channel_id)

        print(f"✅ Learning System: Active and monitoring")
        print(f"   🔄 Will analyze every {self.monitor_interval_hours} hours")
        print(f"   📊 Will check trends every {self.trend_check_interval_hours} hours")

        # Main learning loop
        while self.is_running:
            try:
                self.learning_iteration += 1

                print(f"\n🔄 Learning Iteration #{self.learning_iteration} - {datetime.now().isoformat()}")

                # Step 1: Analyze performance
                await self._analyze_performance_cycle()

                # Step 2: Monitor trends
                await self._monitor_trends_cycle()

                # Step 3: Discover new learnings
                await self._discover_learnings_cycle()

                # Step 4: Update agent strategies
                await self._update_agent_strategies()

                # Step 5: Save learnings
                self._save_learnings()

                # Wait for next cycle
                wait_seconds = min(
                    self.monitor_interval_hours * 3600,
                    self.trend_check_interval_hours * 3600
                )

                print(f"   💤 Next cycle in {wait_seconds/3600:.1f} hours...")
                await asyncio.sleep(wait_seconds)

            except Exception as e:
                print(f"   ⚠️  Learning cycle error: {e}")
                print(f"   🔄 Retrying in 1 hour...")
                await asyncio.sleep(3600)

    def stop_learning(self):
        """Stop the continuous learning loop"""
        print(f"🛑 Autonomous Learning: Stopping system...")
        self.is_running = False

    async def _analyze_performance_cycle(self):
        """Analyze channel performance and learn from results"""
        if not self.analytics_agent:
            print(f"   ⏭️  Skipping performance analysis (no channel set)")
            return

        print(f"   📊 Analyzing performance...")

        # Run analytics
        analysis = await self.analytics_agent.analyze_channel_performance(
            days_back=30,
            min_videos=3
        )

        insights = analysis.get('insights', [])
        summary = analysis.get('summary', {})

        print(f"   ✅ Found {len(insights)} performance insights")

        # Extract high-impact learnings
        for insight in insights:
            if insight.get('confidence', 0) >= 0.7:
                # This is a high-confidence learning
                learning = LearningInsight(
                    insight_type="performance",
                    category=insight.get('insight_type', 'general'),
                    finding=insight.get('finding', ''),
                    confidence=insight.get('confidence', 0),
                    impact_score=8.0,
                    action_items=[insight.get('recommendation', '')],
                    data_points=insight.get('data_points', 0),
                    discovered_at=datetime.now().isoformat()
                )

                self._add_learning(learning)

        self.last_analysis_time = datetime.now()

    async def _monitor_trends_cycle(self):
        """Monitor trending topics and viral opportunities"""
        if not self.ideas_agent:
            print(f"   ⏭️  Skipping trend monitoring (no channel set)")
            return

        print(f"   🔥 Monitoring trends...")

        # Load channel profile to get niche
        active_channel = self.channel_integration.load_active_channel()
        if not active_channel:
            return

        # Discover trending ideas
        ideas = await self.ideas_agent.discover_ideas(
            niche=active_channel.niche,
            num_ideas=20,
            include_trending=True,
            include_evergreen=False
        )

        # Filter for high-potential trends
        hot_trends = [
            idea for idea in ideas
            if idea.trending_score > 0.7 and idea.urgency == "trending_now"
        ]

        print(f"   ✅ Found {len(hot_trends)} hot trending opportunities")

        # Save trends
        self._save_trends(hot_trends)

        # Create learnings from trends
        if len(hot_trends) > 0:
            trend_topics = [idea.topic for idea in hot_trends[:5]]

            learning = LearningInsight(
                insight_type="trend",
                category="topics",
                finding=f"Trending now: {', '.join(trend_topics[:3])}",
                confidence=0.8,
                impact_score=9.0,
                action_items=[f"Create video about: {topic}" for topic in trend_topics[:3]],
                data_points=len(hot_trends),
                discovered_at=datetime.now().isoformat()
            )

            self._add_learning(learning)

    async def _discover_learnings_cycle(self):
        """Deep analysis to discover new techniques and patterns"""
        if not self.client:
            return

        print(f"   🧠 Discovering new learnings...")

        # Load recent learnings
        recent_learnings = self._load_recent_learnings(days=30)

        if len(recent_learnings) < 3:
            print(f"   ⏭️  Not enough data for meta-learning yet")
            return

        try:
            # Meta-analysis: Learn from the learnings
            learnings_summary = "\n".join([
                f"- {l['finding']} (confidence: {l['confidence']:.0%}, impact: {l['impact_score']}/10)"
                for l in recent_learnings[:10]
            ])

            prompt = f"""Analyze these recent learnings from a YouTube channel to discover meta-patterns and high-level strategies.

RECENT LEARNINGS:
{learnings_summary}

Identify:
1. Overarching patterns across learnings
2. High-leverage strategies to implement
3. Things that consistently work
4. New techniques to try based on patterns

Return JSON array of meta-learnings:
[
  {{
    "category": "category",
    "finding": "meta-pattern discovered",
    "confidence": 0.75,
    "impact_score": 8,
    "action_items": ["actionable strategy 1", "actionable strategy 2"]
  }}
]"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text

            # Extract JSON
            start_idx = analysis_text.find('[')
            end_idx = analysis_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                meta_learnings = json.loads(analysis_text[start_idx:end_idx])

                for meta in meta_learnings:
                    learning = LearningInsight(
                        insight_type="pattern",
                        category=meta.get('category', 'general'),
                        finding=meta.get('finding', ''),
                        confidence=meta.get('confidence', 0.7),
                        impact_score=meta.get('impact_score', 7),
                        action_items=meta.get('action_items', []),
                        data_points=len(recent_learnings),
                        discovered_at=datetime.now().isoformat()
                    )

                    self._add_learning(learning)

                print(f"   ✅ Discovered {len(meta_learnings)} meta-patterns")

        except Exception as e:
            print(f"   ⚠️  Meta-learning failed: {e}")

    async def _update_agent_strategies(self):
        """Update agent strategies based on learnings"""
        print(f"   🔧 Updating agent strategies...")

        # Load high-impact learnings
        high_impact = self._load_high_impact_learnings()

        if len(high_impact) == 0:
            print(f"   ⏭️  No high-impact learnings to apply yet")
            return

        # Group by category
        by_category = {}
        for learning in high_impact:
            category = learning.get('category', 'general')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(learning)

        # Save strategy updates for each agent
        strategy_updates = {
            "hooks": [],
            "thumbnails": [],
            "topics": [],
            "retention": [],
            "duration": []
        }

        for category, learnings in by_category.items():
            if category in strategy_updates:
                strategy_updates[category] = [
                    {
                        "finding": l.get('finding', ''),
                        "actions": l.get('action_items', [])
                    }
                    for l in learnings
                ]

        # Save for agents to use
        strategy_file = "data/agent_strategies.json"
        with open(strategy_file, 'w') as f:
            json.dump({
                "updated_at": datetime.now().isoformat(),
                "strategies": strategy_updates
            }, f, indent=2)

        print(f"   ✅ Strategies updated for {len(strategy_updates)} categories")

    def _add_learning(self, learning: LearningInsight):
        """Add a new learning to the database"""
        self.current_learnings = self.current_learnings or []
        self.current_learnings.append(learning)

    def _save_learnings(self):
        """Save learnings to database"""
        if not hasattr(self, 'current_learnings') or not self.current_learnings:
            return

        try:
            # Load existing
            existing = []
            if os.path.exists(self.learnings_db_path):
                with open(self.learnings_db_path, 'r') as f:
                    data = json.load(f)
                    existing = data.get('learnings', [])

            # Add new learnings
            for learning in self.current_learnings:
                existing.append(learning.to_dict())

            # Save
            with open(self.learnings_db_path, 'w') as f:
                json.dump({
                    "learnings": existing,
                    "last_updated": datetime.now().isoformat(),
                    "total_learnings": len(existing)
                }, f, indent=2)

            print(f"   💾 Saved {len(self.current_learnings)} new learnings")

            # Reset
            self.current_learnings = []

        except Exception as e:
            print(f"   ⚠️  Could not save learnings: {e}")

    def _save_trends(self, trends: list):
        """Save discovered trends"""
        try:
            trends_data = {
                "discovered_at": datetime.now().isoformat(),
                "trends": [
                    {
                        "topic": t.topic,
                        "hook_angle": t.hook_angle,
                        "trending_score": t.trending_score,
                        "urgency": t.urgency,
                        "estimated_views": t.estimated_views
                    }
                    for t in trends
                ]
            }

            # Load existing trends
            all_trends = []
            if os.path.exists(self.trends_db_path):
                with open(self.trends_db_path, 'r') as f:
                    data = json.load(f)
                    all_trends = data.get('trend_snapshots', [])

            all_trends.append(trends_data)

            # Keep last 30 days only
            cutoff = datetime.now() - timedelta(days=30)
            all_trends = [
                t for t in all_trends
                if datetime.fromisoformat(t['discovered_at']) > cutoff
            ]

            with open(self.trends_db_path, 'w') as f:
                json.dump({
                    "trend_snapshots": all_trends,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

        except Exception as e:
            print(f"   ⚠️  Could not save trends: {e}")

    def _load_recent_learnings(self, days: int = 30) -> List[Dict]:
        """Load learnings from last N days"""
        try:
            if os.path.exists(self.learnings_db_path):
                with open(self.learnings_db_path, 'r') as f:
                    data = json.load(f)
                    all_learnings = data.get('learnings', [])

                # Filter by date
                cutoff = datetime.now() - timedelta(days=days)
                recent = [
                    l for l in all_learnings
                    if datetime.fromisoformat(l['discovered_at']) > cutoff
                ]

                return recent

        except Exception as e:
            print(f"   ⚠️  Could not load learnings: {e}")

        return []

    def _load_high_impact_learnings(self) -> List[Dict]:
        """Load learnings with high impact scores"""
        try:
            if os.path.exists(self.learnings_db_path):
                with open(self.learnings_db_path, 'r') as f:
                    data = json.load(f)
                    all_learnings = data.get('learnings', [])

                # Filter by impact score and confidence
                high_impact = [
                    l for l in all_learnings
                    if l.get('impact_score', 0) >= 7 and l.get('confidence', 0) >= 0.7
                ]

                # Sort by impact
                high_impact.sort(key=lambda x: x.get('impact_score', 0), reverse=True)

                return high_impact[:20]  # Top 20

        except Exception as e:
            print(f"   ⚠️  Could not load learnings: {e}")

        return []

    def get_learning_report(self) -> str:
        """Generate human-readable learning report"""
        learnings = self._load_recent_learnings(days=7)
        high_impact = self._load_high_impact_learnings()

        report = f"""
# Autonomous Learning System - Report

Generated: {datetime.now().isoformat()}
Iteration: #{self.learning_iteration}
Last Analysis: {self.last_analysis_time}

## Recent Learnings (Last 7 Days)
Total: {len(learnings)}

{self._format_learnings(learnings[:10])}

## High-Impact Strategies
Total: {len(high_impact)}

{self._format_learnings(high_impact[:5])}

## System Status
- Running: {self.is_running}
- Monitor Interval: {self.monitor_interval_hours} hours
- Trend Check Interval: {self.trend_check_interval_hours} hours
- Channel: {self.channel_id or 'Not set'}

---
The system is constantly learning and improving. 🧠
"""

        return report

    def _format_learnings(self, learnings: List[Dict]) -> str:
        """Format learnings for report"""
        if len(learnings) == 0:
            return "No learnings yet."

        formatted = []
        for l in learnings:
            formatted.append(f"""
### {l.get('category', 'General').title()}
- **Finding**: {l.get('finding', '')}
- **Confidence**: {l.get('confidence', 0):.0%}
- **Impact**: {l.get('impact_score', 0)}/10
- **Actions**: {', '.join(l.get('action_items', [])[:2])}
""")

        return "\n".join(formatted)


# Initialize global learning system
_global_learning_system = None


def get_learning_system(channel_id: Optional[str] = None) -> AutonomousLearningSystem:
    """Get or create the global learning system"""
    global _global_learning_system

    if _global_learning_system is None:
        _global_learning_system = AutonomousLearningSystem(channel_id=channel_id)

    return _global_learning_system
