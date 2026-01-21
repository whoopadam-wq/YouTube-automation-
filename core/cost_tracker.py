"""
Cost Tracker
Tracks API usage costs per channel and enforces budget caps.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum


class CostCategory(Enum):
    """Cost categories."""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    VOICE_SYNTHESIS = "voice_synthesis"
    CHARACTER_GENERATION = "character_generation"
    OTHER = "other"


class CostTracker:
    """
    Tracks API costs and enforces budget limits.
    """

    def __init__(self, config_manager):
        """Initialize cost tracker."""
        self.config = config_manager
        self.db_path = config_manager.data_path / "database" / "automation.db"
        self._init_database()

    def _init_database(self):
        """Initialize cost tracking tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                video_id TEXT,
                category TEXT NOT NULL,
                provider TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_costs_channel ON costs(channel_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_costs_timestamp ON costs(timestamp)")

        conn.commit()
        conn.close()

    def record_cost(
        self,
        channel_id: str,
        category: CostCategory,
        provider: str,
        amount: float,
        video_id: Optional[str] = None,
        metadata: Optional[str] = None
    ):
        """Record a cost entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO costs (
                channel_id, video_id, category, provider, amount, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (channel_id, video_id, category.value, provider, amount, metadata))

        conn.commit()
        conn.close()

    def get_channel_costs_today(self, channel_id: str) -> float:
        """Get total costs for a channel today."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date()

        cursor.execute("""
            SELECT SUM(amount) FROM costs
            WHERE channel_id = ?
            AND DATE(timestamp) = ?
        """, (channel_id, today))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def get_global_costs_today(self) -> float:
        """Get total costs across all channels today."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        today = datetime.now().date()

        cursor.execute("""
            SELECT SUM(amount) FROM costs
            WHERE DATE(timestamp) = ?
        """, (today,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def get_channel_costs_month(self, channel_id: str) -> float:
        """Get total costs for a channel this month."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        first_day = datetime.now().replace(day=1).date()

        cursor.execute("""
            SELECT SUM(amount) FROM costs
            WHERE channel_id = ?
            AND DATE(timestamp) >= ?
        """, (channel_id, first_day))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def get_global_costs_month(self) -> float:
        """Get total costs across all channels this month."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        first_day = datetime.now().replace(day=1).date()

        cursor.execute("""
            SELECT SUM(amount) FROM costs
            WHERE DATE(timestamp) >= ?
        """, (first_day,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def check_budget_limit(self, channel_id: str) -> tuple[bool, str]:
        """
        Check if channel is within budget.

        Returns:
            (allowed, message) - True if under budget, False if over
        """
        # Get channel config
        channel = self.config.get_channel(channel_id)
        if not channel:
            return False, f"Channel {channel_id} not found"

        # Check daily channel limit
        daily_cost = self.get_channel_costs_today(channel_id)
        if daily_cost >= channel.api_cost_cap_per_day:
            return False, f"Channel daily budget exceeded: ${daily_cost:.2f} / ${channel.api_cost_cap_per_day:.2f}"

        # Check global daily limit
        global_daily = self.config.get_system_setting('cost_management.global_daily_cost_cap', 50.0)
        global_daily_cost = self.get_global_costs_today()
        if global_daily_cost >= global_daily:
            return False, f"Global daily budget exceeded: ${global_daily_cost:.2f} / ${global_daily:.2f}"

        # Check global monthly limit
        global_monthly = self.config.get_system_setting('cost_management.global_monthly_cost_cap', 1000.0)
        global_monthly_cost = self.get_global_costs_month()
        if global_monthly_cost >= global_monthly:
            return False, f"Global monthly budget exceeded: ${global_monthly_cost:.2f} / ${global_monthly:.2f}"

        return True, "Within budget"

    def get_cost_breakdown(
        self,
        channel_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, float]:
        """Get cost breakdown by category."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        if channel_id:
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM costs
                WHERE channel_id = ? AND DATE(timestamp) >= ?
                GROUP BY category
            """, (channel_id, cutoff_date))
        else:
            cursor.execute("""
                SELECT category, SUM(amount) as total
                FROM costs
                WHERE DATE(timestamp) >= ?
                GROUP BY category
            """, (cutoff_date,))

        rows = cursor.fetchall()
        conn.close()

        return {category: total for category, total in rows}

    def get_video_cost(self, video_id: str) -> float:
        """Get total cost for a specific video."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(amount) FROM costs
            WHERE video_id = ?
        """, (video_id,))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] else 0.0

    def estimate_video_cost(
        self,
        content_type: str,
        channel_config: Dict
    ) -> float:
        """
        Estimate cost for a video based on content type.

        Args:
            content_type: 'long_form' or 'short_form'
            channel_config: Channel configuration

        Returns:
            Estimated cost in USD
        """
        cost_config = self.config.get_system_setting('cost_management.cost_per_generation', {})

        # Base costs
        script_cost = cost_config.get('text_generation', 0.05)
        voice_cost = cost_config.get('voice_synthesis', 0.15)

        if content_type == 'long_form':
            # Long form: more scenes, more images/videos
            num_scenes = channel_config.get('target_long_duration', 10) * 3
            image_cost = num_scenes * cost_config.get('image_generation', 0.10)
            video_cost = num_scenes * cost_config.get('video_generation', 2.00)

            # Character cost if enabled
            character_cost = 0
            if channel_config.get('use_channel_character', False):
                character_cost = cost_config.get('character_generation', 0.50)

            total = script_cost + image_cost + video_cost + voice_cost + character_cost

        else:  # short_form
            # Shorts: fewer scenes
            num_scenes = 3
            image_cost = num_scenes * cost_config.get('image_generation', 0.10)
            video_cost = num_scenes * cost_config.get('video_generation', 2.00)

            total = script_cost + image_cost + video_cost + voice_cost

        return total

    def get_daily_report(self, channel_id: Optional[str] = None) -> Dict:
        """Get daily cost report."""
        return {
            'channel_id': channel_id or 'all',
            'date': datetime.now().date().isoformat(),
            'total_cost': self.get_channel_costs_today(channel_id) if channel_id else self.get_global_costs_today(),
            'breakdown': self.get_cost_breakdown(channel_id, days=1)
        }

    def get_alerts(self) -> List[Dict]:
        """Get cost alerts for channels nearing limits."""
        alerts = []

        threshold = self.config.get_system_setting('cost_management.alert_threshold_percentage', 80) / 100

        for channel in self.config.get_active_channels():
            daily_cost = self.get_channel_costs_today(channel.channel_id)
            limit = channel.api_cost_cap_per_day

            if daily_cost >= limit * threshold:
                alerts.append({
                    'channel_id': channel.channel_id,
                    'channel_name': channel.channel_name,
                    'current': daily_cost,
                    'limit': limit,
                    'percentage': (daily_cost / limit) * 100
                })

        return alerts
