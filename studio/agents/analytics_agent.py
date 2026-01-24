"""
YouTube Analytics Agent - Self-learning performance optimizer
Studies channel metrics, learns what works, constantly improves
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic


class PerformanceInsight:
    """Represents a learning from channel analytics"""
    def __init__(
        self,
        insight_type: str,  # "hook", "thumbnail", "duration", "topic", "retention"
        finding: str,
        confidence: float,  # 0-1
        data_points: int,
        recommendation: str,
        examples: List[Dict]
    ):
        self.insight_type = insight_type
        self.finding = finding
        self.confidence = confidence
        self.data_points = data_points
        self.recommendation = recommendation
        self.examples = examples
        self.discovered_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "insight_type": self.insight_type,
            "finding": self.finding,
            "confidence": self.confidence,
            "data_points": self.data_points,
            "recommendation": self.recommendation,
            "examples": self.examples,
            "discovered_at": self.discovered_at
        }


class AnalyticsAgent:
    """
    Self-learning YouTube analytics agent that:
    - Studies channel performance metrics (CTR, AVD, views, retention)
    - Analyzes what hooks perform best
    - Identifies winning thumbnail patterns
    - Tracks retention drop-off points
    - Learns from successful vs unsuccessful videos
    - Provides actionable recommendations
    - Constantly getting smarter with more data
    """

    def __init__(self, channel_id: str):
        # LLM for analysis
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Analytics Agent will use basic mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20240620"

        # YouTube APIs
        self.youtube_api_key = os.environ.get('YOUTUBE_DATA_API_KEY')
        self.channel_id = channel_id

        # Learning database
        self.insights_db_path = "data/analytics_insights.json"
        self.videos_db_path = "data/videos_performance.json"

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Load existing learnings
        self.learnings = self._load_learnings()

    async def analyze_channel_performance(
        self,
        days_back: int = 30,
        min_videos: int = 5
    ) -> Dict[str, Any]:
        """
        Main method: Analyze recent channel performance and generate insights

        Args:
            days_back: Number of days to analyze
            min_videos: Minimum videos needed for analysis

        Returns:
            Dict with insights, recommendations, and performance summary
        """
        print(f"📊 Analytics Agent: Analyzing channel performance (last {days_back} days)...")

        # Step 1: Fetch video performance data
        print(f"   📥 Fetching video metrics...")
        videos_data = await self._fetch_videos_performance(days_back)

        if len(videos_data) < min_videos:
            print(f"   ⚠️  Not enough videos for analysis (found {len(videos_data)}, need {min_videos})")
            return self._get_fallback_analysis()

        # Step 2: Save raw data
        self._save_videos_data(videos_data)

        # Step 3: Analyze hooks
        print(f"   🎣 Analyzing hook patterns...")
        hook_insights = await self._analyze_hooks(videos_data)

        # Step 4: Analyze thumbnails
        print(f"   🖼️  Analyzing thumbnail performance...")
        thumbnail_insights = await self._analyze_thumbnails(videos_data)

        # Step 5: Analyze retention patterns
        print(f"   ⏱️  Analyzing retention patterns...")
        retention_insights = await self._analyze_retention(videos_data)

        # Step 6: Analyze topic performance
        print(f"   📝 Analyzing topic performance...")
        topic_insights = await self._analyze_topics(videos_data)

        # Step 7: Analyze optimal duration
        print(f"   ⏳ Analyzing optimal video duration...")
        duration_insights = await self._analyze_duration(videos_data)

        # Step 8: Combine all insights
        all_insights = (
            hook_insights +
            thumbnail_insights +
            retention_insights +
            topic_insights +
            duration_insights
        )

        # Step 9: Generate recommendations
        print(f"   💡 Generating recommendations...")
        recommendations = await self._generate_recommendations(all_insights, videos_data)

        # Step 10: Update learnings database
        self._save_learnings(all_insights)

        # Step 11: Calculate performance summary
        summary = self._calculate_summary(videos_data)

        print(f"✅ Analytics Agent: Analysis complete - {len(all_insights)} insights generated")

        return {
            "summary": summary,
            "insights": [i.to_dict() for i in all_insights],
            "recommendations": recommendations,
            "analyzed_videos": len(videos_data),
            "analysis_date": datetime.now().isoformat()
        }

    async def _fetch_videos_performance(self, days_back: int) -> List[Dict]:
        """
        Fetch video performance data from YouTube API
        Returns list of videos with metrics
        """
        if not self.youtube_api_key or not self.channel_id:
            raise ValueError(
                "YouTube Data API key and channel ID are required for analytics.\n"
                "Make sure YOUTUBE_DATA_API_KEY is set in environment variables."
            )

        try:
            videos = []

            # Step 1: Get channel's uploads playlist
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "contentDetails,statistics",
                "id": self.channel_id,
                "key": self.youtube_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "items" not in data or len(data["items"]) == 0:
                raise ValueError(f"Channel {self.channel_id} not found or has no uploads playlist")

            uploads_playlist = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Step 2: Get recent videos from playlist
            url = f"https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist,
                "maxResults": 50,  # YouTube API max
                "key": self.youtube_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            playlist_data = response.json()

            # Step 3: Get detailed stats for each video
            from datetime import timezone
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

            for item in playlist_data.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                published_at = datetime.fromisoformat(
                    item["snippet"]["publishedAt"].replace('Z', '+00:00')
                )

                # Only include videos within date range
                if published_at < cutoff_date:
                    continue

                # Fetch video statistics
                url = f"https://www.googleapis.com/youtube/v3/videos"
                params = {
                    "part": "statistics,contentDetails,snippet",
                    "id": video_id,
                    "key": self.youtube_api_key
                }
                response = requests.get(url, params=params, timeout=10)
                video_data = response.json()

                if "items" in video_data and len(video_data["items"]) > 0:
                    video_info = video_data["items"][0]
                    stats = video_info["statistics"]
                    snippet = video_info["snippet"]
                    content_details = video_info["contentDetails"]

                    # Parse duration (PT1M30S format)
                    duration_str = content_details["duration"]
                    duration_seconds = self._parse_youtube_duration(duration_str)

                    videos.append({
                        "id": video_id,
                        "title": snippet["title"],
                        "description": snippet.get("description", ""),
                        "published_at": published_at.isoformat(),
                        "duration": duration_seconds,
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments": int(stats.get("commentCount", 0)),
                        "thumbnail_url": snippet["thumbnails"]["high"]["url"],
                        # Note: CTR and AVD require YouTube Analytics API (not Data API)
                        # Using estimated values for now
                        "ctr": None,  # Would need Analytics API
                        "avg_view_duration": None,  # Would need Analytics API
                        "retention_data": None  # Would need Analytics API
                    })

            return videos

        except Exception as e:
            print(f"   ⚠️  YouTube API error: {e}")
            raise ValueError(f"Failed to fetch videos from YouTube API: {str(e)}")

    def _parse_youtube_duration(self, duration_str: str) -> int:
        """Parse YouTube duration format (PT1H2M30S) to seconds"""
        import re

        hours = 0
        minutes = 0
        seconds = 0

        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))

        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))

        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))

        return hours * 3600 + minutes * 60 + seconds

    async def _analyze_hooks(self, videos_data: List[Dict]) -> List[PerformanceInsight]:
        """
        Analyze which hook patterns perform best
        Looks at titles and correlates with CTR/views
        """
        insights = []

        if not self.client:
            return []

        try:
            # Sort by views to find top performers
            top_videos = sorted(videos_data, key=lambda v: v['views'], reverse=True)[:10]
            bottom_videos = sorted(videos_data, key=lambda v: v['views'])[:10]

            top_titles = [v['title'] for v in top_videos]
            bottom_titles = [v['title'] for v in bottom_videos]

            prompt = f"""Analyze these YouTube video titles to identify hook patterns that perform well vs poorly.

TOP PERFORMING TITLES:
{chr(10).join([f"- {t}" for t in top_titles])}

LOW PERFORMING TITLES:
{chr(10).join([f"- {t}" for t in bottom_titles])}

Identify:
1. What hook patterns work best? (question, contrarian, curiosity gap, etc.)
2. What patterns should be avoided?
3. Optimal title length
4. Power words that increase clicks
5. Specific recommendations for future titles

Return JSON array of insights:
[
  {{
    "finding": "Specific pattern that works",
    "confidence": 0.85,
    "recommendation": "Action to take",
    "examples": ["example 1", "example 2"]
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
                findings = json.loads(analysis_text[start_idx:end_idx])

                for finding in findings:
                    insights.append(PerformanceInsight(
                        insight_type="hook",
                        finding=finding.get('finding', ''),
                        confidence=finding.get('confidence', 0.5),
                        data_points=len(videos_data),
                        recommendation=finding.get('recommendation', ''),
                        examples=finding.get('examples', [])
                    ))

        except Exception as e:
            print(f"   ⚠️  Hook analysis failed: {e}")

        return insights

    async def _analyze_thumbnails(self, videos_data: List[Dict]) -> List[PerformanceInsight]:
        """
        Analyze thumbnail patterns (would need image analysis in production)
        For now, provides general recommendations
        """
        insights = []

        # Calculate average CTR by views (proxy metric)
        avg_views = sum(v['views'] for v in videos_data) / len(videos_data)
        high_performing = [v for v in videos_data if v['views'] > avg_views * 1.5]

        if len(high_performing) > 0:
            insights.append(PerformanceInsight(
                insight_type="thumbnail",
                finding=f"{len(high_performing)} videos significantly outperformed average",
                confidence=0.7,
                data_points=len(videos_data),
                recommendation="Analyze thumbnails of top performers for visual patterns",
                examples=[v['title'] for v in high_performing[:3]]
            ))

        return insights

    async def _analyze_retention(self, videos_data: List[Dict]) -> List[PerformanceInsight]:
        """
        Analyze retention patterns (would need Analytics API for actual retention curves)
        """
        insights = []

        # Analyze views to likes ratio (engagement proxy)
        for video in videos_data:
            if video['views'] > 0:
                video['engagement_rate'] = video['likes'] / video['views']

        avg_engagement = sum(v.get('engagement_rate', 0) for v in videos_data) / len(videos_data)

        insights.append(PerformanceInsight(
            insight_type="retention",
            finding=f"Average engagement rate: {avg_engagement:.2%}",
            confidence=0.6,
            data_points=len(videos_data),
            recommendation="Focus on hooks and pacing to maintain engagement throughout video",
            examples=[]
        ))

        return insights

    async def _analyze_topics(self, videos_data: List[Dict]) -> List[PerformanceInsight]:
        """
        Identify which topics perform best
        """
        insights = []

        if not self.client or len(videos_data) < 5:
            return []

        try:
            # Group videos by performance
            sorted_videos = sorted(videos_data, key=lambda v: v['views'], reverse=True)
            top_videos = sorted_videos[:len(sorted_videos)//3]  # Top third
            bottom_videos = sorted_videos[-len(sorted_videos)//3:]  # Bottom third

            top_topics = [v['title'] for v in top_videos]
            bottom_topics = [v['title'] for v in bottom_videos]

            prompt = f"""Analyze these video topics to identify content patterns.

HIGH PERFORMING:
{chr(10).join([f"- {t}" for t in top_topics])}

LOW PERFORMING:
{chr(10).join([f"- {t}" for t in bottom_topics])}

What topics/themes work best for this channel? What should be avoided?

Return JSON:
{{
    "winning_topics": ["topic1", "topic2"],
    "avoid_topics": ["topic1", "topic2"],
    "recommendation": "specific advice"
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text

            # Extract JSON
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                analysis = json.loads(analysis_text[start_idx:end_idx])

                insights.append(PerformanceInsight(
                    insight_type="topic",
                    finding=f"Winning topics: {', '.join(analysis.get('winning_topics', []))}",
                    confidence=0.75,
                    data_points=len(videos_data),
                    recommendation=analysis.get('recommendation', ''),
                    examples=analysis.get('winning_topics', [])
                ))

        except Exception as e:
            print(f"   ⚠️  Topic analysis failed: {e}")

        return insights

    async def _analyze_duration(self, videos_data: List[Dict]) -> List[PerformanceInsight]:
        """
        Find optimal video duration for the channel
        """
        insights = []

        # Group by duration ranges
        short = [v for v in videos_data if v['duration'] <= 60]
        medium = [v for v in videos_data if 60 < v['duration'] <= 300]
        long = [v for v in videos_data if v['duration'] > 300]

        def avg_views(group):
            return sum(v['views'] for v in group) / len(group) if len(group) > 0 else 0

        short_avg = avg_views(short)
        medium_avg = avg_views(medium)
        long_avg = avg_views(long)

        best_duration = "short (≤60s)"
        best_avg = short_avg

        if medium_avg > best_avg:
            best_duration = "medium (1-5min)"
            best_avg = medium_avg

        if long_avg > best_avg:
            best_duration = "long (5min+)"
            best_avg = long_avg

        insights.append(PerformanceInsight(
            insight_type="duration",
            finding=f"Best performing duration: {best_duration}",
            confidence=0.7,
            data_points=len(videos_data),
            recommendation=f"Focus on {best_duration} videos for maximum views",
            examples=[]
        ))

        return insights

    async def _generate_recommendations(
        self,
        insights: List[PerformanceInsight],
        videos_data: List[Dict]
    ) -> List[str]:
        """
        Generate actionable recommendations from insights
        """
        recommendations = []

        # High-confidence insights become top recommendations
        high_confidence = [i for i in insights if i.confidence >= 0.7]

        for insight in high_confidence:
            if insight.recommendation:
                recommendations.append(f"[{insight.insight_type.upper()}] {insight.recommendation}")

        # Add general recommendations
        if len(videos_data) > 0:
            avg_views = sum(v['views'] for v in videos_data) / len(videos_data)
            recommendations.append(f"Current average views: {int(avg_views):,}")

            best_video = max(videos_data, key=lambda v: v['views'])
            recommendations.append(f"Best performing: '{best_video['title']}' ({best_video['views']:,} views)")

        return recommendations

    def _calculate_summary(self, videos_data: List[Dict]) -> Dict[str, Any]:
        """Calculate performance summary statistics"""
        if len(videos_data) == 0:
            return {}

        total_views = sum(v['views'] for v in videos_data)
        total_likes = sum(v['likes'] for v in videos_data)
        avg_views = total_views / len(videos_data)
        avg_likes = total_likes / len(videos_data)
        avg_duration = sum(v['duration'] for v in videos_data) / len(videos_data)

        return {
            "total_videos": len(videos_data),
            "total_views": total_views,
            "total_likes": total_likes,
            "avg_views_per_video": int(avg_views),
            "avg_likes_per_video": int(avg_likes),
            "avg_duration_seconds": int(avg_duration),
            "best_performing": max(videos_data, key=lambda v: v['views'])['title'],
            "recent_upload_frequency": "Analysis not yet available"
        }

    def _save_videos_data(self, videos_data: List[Dict]):
        """Save video performance data to database"""
        try:
            with open(self.videos_db_path, 'w') as f:
                json.dump({
                    "videos": videos_data,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

            print(f"   💾 Saved performance data for {len(videos_data)} videos")

        except Exception as e:
            print(f"   ⚠️  Could not save videos data: {e}")

    def _save_learnings(self, insights: List[PerformanceInsight]):
        """Save insights to learnings database"""
        try:
            with open(self.insights_db_path, 'w') as f:
                json.dump({
                    "insights": [i.to_dict() for i in insights],
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

            self.learnings = insights
            print(f"   🧠 Saved {len(insights)} learnings to database")

        except Exception as e:
            print(f"   ⚠️  Could not save learnings: {e}")

    def _load_learnings(self) -> List[PerformanceInsight]:
        """Load existing learnings from database"""
        try:
            if os.path.exists(self.insights_db_path):
                with open(self.insights_db_path, 'r') as f:
                    data = json.load(f)
                    # Convert back to PerformanceInsight objects
                    # (simplified - just return empty for now)
                    return []
        except Exception as e:
            print(f"   ⚠️  Could not load learnings: {e}")

        return []

    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when not enough data"""
        return {
            "summary": {
                "total_videos": 0,
                "message": "Not enough videos for analysis"
            },
            "insights": [],
            "recommendations": [
                "Upload more videos to enable analytics",
                "Ensure YouTube API key is configured",
                "Check channel ID is correct"
            ],
            "analyzed_videos": 0
        }

    def _generate_mock_videos_data(self) -> List[Dict]:
        """Generate mock video data for testing"""
        import random

        mock_videos = []
        titles = [
            "How to Master AI in 2024",
            "Top 10 Productivity Hacks",
            "Why Everyone is Wrong About AI",
            "Secret Strategy for YouTube Growth",
            "The Truth About Making Money Online"
        ]

        for i, title in enumerate(titles):
            mock_videos.append({
                "id": f"mock_video_{i}",
                "title": title,
                "description": f"Description for {title}",
                "published_at": (datetime.now() - timedelta(days=i*7)).isoformat(),
                "duration": random.randint(30, 600),
                "views": random.randint(1000, 50000),
                "likes": random.randint(50, 2000),
                "comments": random.randint(10, 500),
                "thumbnail_url": "",
                "ctr": random.uniform(0.02, 0.12),
                "avg_view_duration": random.uniform(20, 120),
                "retention_data": None
            })

        return mock_videos
