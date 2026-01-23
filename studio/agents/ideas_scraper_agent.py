"""
Video Ideas Scraper Agent - Autonomous topic discovery and research
Finds trending topics, understands channel style, tracks history
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic


class VideoIdea:
    """Represents a video idea with metadata"""
    def __init__(
        self,
        topic: str,
        hook_angle: str,
        trending_score: float,
        research_notes: str,
        competitor_examples: List[str],
        estimated_views: str,
        suggested_duration: int,
        urgency: str  # "trending_now", "evergreen", "seasonal"
    ):
        self.topic = topic
        self.hook_angle = hook_angle
        self.trending_score = trending_score
        self.research_notes = research_notes
        self.competitor_examples = competitor_examples
        self.estimated_views = estimated_views
        self.suggested_duration = suggested_duration
        self.urgency = urgency
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "topic": self.topic,
            "hook_angle": self.hook_angle,
            "trending_score": self.trending_score,
            "research_notes": self.research_notes,
            "competitor_examples": self.competitor_examples,
            "estimated_views": self.estimated_views,
            "suggested_duration": self.suggested_duration,
            "urgency": self.urgency,
            "created_at": self.created_at
        }


class IdeasScraperAgent:
    """
    Autonomous video idea discovery agent that:
    - Monitors trending topics in your niche
    - Analyzes what's working for competitors
    - Understands your channel's style and voice
    - Tracks video history to avoid duplicates
    - Constantly researching and finding opportunities
    - Scores ideas by viral potential
    """

    def __init__(self, channel_id: Optional[str] = None):
        # LLM for analysis
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Ideas Scraper will use basic mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # Research APIs
        self.serper_api_key = os.environ.get('SERPER_API_KEY')
        self.youtube_api_key = os.environ.get('YOUTUBE_DATA_API_KEY')

        # Channel context
        self.channel_id = channel_id
        self.channel_profile = None  # Loaded from analysis

        # History tracking
        self.ideas_db_path = "data/video_ideas_history.json"
        self.produced_videos_path = "data/produced_videos.json"

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

    async def discover_ideas(
        self,
        niche: str,
        num_ideas: int = 10,
        include_trending: bool = True,
        include_evergreen: bool = True
    ) -> List[VideoIdea]:
        """
        Main method: Discover and rank video ideas

        Args:
            niche: The content niche (e.g., "tech reviews", "cooking", "finance")
            num_ideas: Number of ideas to generate
            include_trending: Include trending topics
            include_evergreen: Include evergreen content

        Returns:
            List of VideoIdea objects ranked by potential
        """
        print(f"🔍 Ideas Scraper: Discovering video ideas for '{niche}'...")

        # Step 1: Load channel profile if available
        if self.channel_id:
            print(f"   📊 Analyzing channel style...")
            self.channel_profile = await self._analyze_channel_style()

        # Step 2: Load history to avoid duplicates
        print(f"   📚 Loading video history...")
        produced_topics = self._load_produced_topics()

        # Step 3: Research trending topics
        trending_topics = []
        if include_trending:
            print(f"   🔥 Researching trending topics...")
            trending_topics = await self._research_trending_topics(niche)

        # Step 4: Research evergreen opportunities
        evergreen_topics = []
        if include_evergreen:
            print(f"   ♾️  Finding evergreen opportunities...")
            evergreen_topics = await self._research_evergreen_topics(niche)

        # Step 5: Combine and filter duplicates
        all_raw_topics = trending_topics + evergreen_topics
        filtered_topics = self._filter_duplicates(all_raw_topics, produced_topics)

        # Step 6: Deep analysis on each topic
        print(f"   🧠 Analyzing {len(filtered_topics)} potential ideas...")
        video_ideas = []

        for topic_data in filtered_topics[:num_ideas * 2]:  # Analyze more than needed
            idea = await self._analyze_topic_deeply(topic_data, niche)
            if idea:
                video_ideas.append(idea)

        # Step 7: Rank by viral potential
        print(f"   📈 Ranking ideas by viral potential...")
        ranked_ideas = self._rank_ideas(video_ideas)

        # Step 8: Save to ideas database
        self._save_ideas_to_db(ranked_ideas[:num_ideas])

        print(f"✅ Ideas Scraper: Found {len(ranked_ideas[:num_ideas])} high-potential ideas")
        return ranked_ideas[:num_ideas]

    async def _analyze_channel_style(self) -> Dict[str, Any]:
        """
        Analyze the channel's existing videos to understand style
        Returns profile with: tone, topics, avg_duration, common_hooks, etc.
        """
        if not self.youtube_api_key or not self.channel_id:
            return self._get_default_profile()

        try:
            # Fetch recent videos from channel
            videos = self._fetch_channel_videos(self.channel_id, max_results=20)

            if not videos or not self.client:
                return self._get_default_profile()

            # Analyze with LLM
            videos_summary = "\n".join([
                f"- {v['title']} ({v['duration']}s, {v['views']} views)"
                for v in videos[:10]
            ])

            prompt = f"""Analyze this YouTube channel's content style based on recent videos:

{videos_summary}

Identify:
1. Primary content niche and sub-topics
2. Tone and voice (casual, educational, entertaining, etc.)
3. Average video duration preference
4. Common hook patterns in titles
5. Target audience characteristics
6. What makes their content unique

Return JSON:
{{
    "niche": "main niche",
    "sub_topics": ["topic1", "topic2"],
    "tone": "description",
    "avg_duration": seconds,
    "hook_patterns": ["pattern1", "pattern2"],
    "target_audience": "description",
    "unique_angle": "what makes them different"
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            profile_text = response.content[0].text
            # Extract JSON
            start_idx = profile_text.find('{')
            end_idx = profile_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                profile = json.loads(profile_text[start_idx:end_idx])
                return profile

        except Exception as e:
            print(f"   ⚠️  Channel analysis failed: {e}")

        return self._get_default_profile()

    def _fetch_channel_videos(self, channel_id: str, max_results: int = 20) -> List[Dict]:
        """Fetch recent videos from YouTube Data API"""
        if not self.youtube_api_key:
            return []

        try:
            # Get uploads playlist ID
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "contentDetails",
                "id": channel_id,
                "key": self.youtube_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "items" not in data or len(data["items"]) == 0:
                return []

            uploads_playlist = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Get videos from uploads playlist
            url = f"https://www.googleapis.com/youtube/v3/playlistItems"
            params = {
                "part": "snippet",
                "playlistId": uploads_playlist,
                "maxResults": max_results,
                "key": self.youtube_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            videos = []
            for item in data.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                videos.append({
                    "id": video_id,
                    "title": item["snippet"]["title"],
                    "duration": 0,  # Would need additional API call
                    "views": 0  # Would need additional API call
                })

            return videos

        except Exception as e:
            print(f"   ⚠️  YouTube API error: {e}")
            return []

    async def _research_trending_topics(self, niche: str) -> List[Dict]:
        """
        Research what's trending RIGHT NOW in the niche
        Returns list of topic data with trending scores
        """
        trending = []

        # Use Serper API to search trending content
        if self.serper_api_key:
            try:
                # Search for recent viral content
                queries = [
                    f"{niche} viral 2024",
                    f"{niche} trending now",
                    f"best {niche} videos this month",
                    f"{niche} breaking news"
                ]

                for query in queries:
                    headers = {
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    }
                    payload = {"q": query, "num": 10}

                    response = requests.post(
                        "https://google.serper.dev/search",
                        headers=headers,
                        json=payload,
                        timeout=10
                    )

                    if response.status_code == 200:
                        results = response.json()
                        for result in results.get('organic', [])[:5]:
                            trending.append({
                                "topic": result.get('title', ''),
                                "snippet": result.get('snippet', ''),
                                "source_url": result.get('link', ''),
                                "type": "trending",
                                "discovered_at": datetime.now().isoformat()
                            })

            except Exception as e:
                print(f"   ⚠️  Serper API error: {e}")

        # Fallback: Generate trending topics based on niche
        if len(trending) == 0:
            trending = self._generate_fallback_trending(niche)

        return trending

    async def _research_evergreen_topics(self, niche: str) -> List[Dict]:
        """
        Find evergreen content opportunities that always perform well
        """
        evergreen = []

        # Common evergreen patterns
        evergreen_patterns = [
            f"How to {niche} for beginners",
            f"{niche} mistakes to avoid",
            f"Best {niche} tips and tricks",
            f"{niche} explained simply",
            f"Ultimate {niche} guide"
        ]

        for pattern in evergreen_patterns:
            evergreen.append({
                "topic": pattern,
                "snippet": f"Evergreen content opportunity: {pattern}",
                "source_url": "",
                "type": "evergreen",
                "discovered_at": datetime.now().isoformat()
            })

        return evergreen

    def _filter_duplicates(
        self,
        raw_topics: List[Dict],
        produced_topics: List[str]
    ) -> List[Dict]:
        """
        Filter out topics that are too similar to already produced content
        """
        filtered = []

        for topic_data in raw_topics:
            topic = topic_data.get('topic', '').lower()

            # Check if too similar to existing content
            is_duplicate = False
            for produced in produced_topics:
                # Simple similarity check (could be enhanced with embeddings)
                if self._similarity_score(topic, produced.lower()) > 0.7:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(topic_data)

        return filtered

    def _similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity score between two texts
        Returns 0.0 to 1.0
        """
        words1 = set(text1.split())
        words2 = set(text2.split())

        if len(words1) == 0 or len(words2) == 0:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def _analyze_topic_deeply(
        self,
        topic_data: Dict,
        niche: str
    ) -> Optional[VideoIdea]:
        """
        Deep analysis of a single topic to create full VideoIdea
        """
        if not self.client:
            # Fallback: Create basic idea
            return VideoIdea(
                topic=topic_data.get('topic', ''),
                hook_angle="Interesting angle on this topic",
                trending_score=0.5,
                research_notes=topic_data.get('snippet', ''),
                competitor_examples=[],
                estimated_views="10K-50K",
                suggested_duration=60,
                urgency=topic_data.get('type', 'evergreen')
            )

        try:
            prompt = f"""Analyze this video topic idea for a {niche} channel:

Topic: {topic_data.get('topic', '')}
Context: {topic_data.get('snippet', '')}
Type: {topic_data.get('type', 'unknown')}

Provide deep analysis:
1. Best hook angle to make this topic irresistible
2. Why this topic has viral potential (0-100 score)
3. Research notes on what to cover
4. Estimated view range based on niche
5. Suggested duration (15s, 30s, 60s, 5min, etc.)
6. Urgency (trending_now, seasonal, evergreen)

Return JSON:
{{
    "hook_angle": "specific angle that creates curiosity",
    "trending_score": 75,
    "research_notes": "key points to cover",
    "estimated_views": "50K-200K",
    "suggested_duration": 60,
    "urgency": "trending_now"
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

                return VideoIdea(
                    topic=topic_data.get('topic', ''),
                    hook_angle=analysis.get('hook_angle', ''),
                    trending_score=analysis.get('trending_score', 50) / 100.0,
                    research_notes=analysis.get('research_notes', ''),
                    competitor_examples=[],  # TODO: Add competitor research
                    estimated_views=analysis.get('estimated_views', 'Unknown'),
                    suggested_duration=analysis.get('suggested_duration', 60),
                    urgency=analysis.get('urgency', 'evergreen')
                )

        except Exception as e:
            print(f"   ⚠️  Topic analysis failed: {e}")

        return None

    def _rank_ideas(self, ideas: List[VideoIdea]) -> List[VideoIdea]:
        """
        Rank ideas by viral potential
        Considers: trending_score, urgency, channel fit
        """
        def score_idea(idea: VideoIdea) -> float:
            score = idea.trending_score * 100

            # Urgency bonus
            if idea.urgency == "trending_now":
                score += 30
            elif idea.urgency == "seasonal":
                score += 15

            # Channel fit bonus (if we have profile)
            if self.channel_profile:
                # TODO: Add similarity check with channel_profile
                pass

            return score

        return sorted(ideas, key=score_idea, reverse=True)

    def _load_produced_topics(self) -> List[str]:
        """Load list of topics that have already been produced"""
        try:
            if os.path.exists(self.produced_videos_path):
                with open(self.produced_videos_path, 'r') as f:
                    data = json.load(f)
                    return [v.get('topic', '') for v in data.get('videos', [])]
        except Exception as e:
            print(f"   ⚠️  Could not load produced videos: {e}")

        return []

    def _save_ideas_to_db(self, ideas: List[VideoIdea]):
        """Save discovered ideas to database for tracking"""
        try:
            # Load existing ideas
            existing = []
            if os.path.exists(self.ideas_db_path):
                with open(self.ideas_db_path, 'r') as f:
                    existing = json.load(f)

            # Append new ideas
            for idea in ideas:
                existing.append(idea.to_dict())

            # Save back
            with open(self.ideas_db_path, 'w') as f:
                json.dump(existing, f, indent=2)

            print(f"   💾 Saved {len(ideas)} ideas to database")

        except Exception as e:
            print(f"   ⚠️  Could not save ideas: {e}")

    def mark_topic_as_produced(self, topic: str, video_id: str):
        """Mark a topic as produced to avoid duplicates"""
        try:
            produced = []
            if os.path.exists(self.produced_videos_path):
                with open(self.produced_videos_path, 'r') as f:
                    data = json.load(f)
                    produced = data.get('videos', [])

            produced.append({
                "topic": topic,
                "video_id": video_id,
                "produced_at": datetime.now().isoformat()
            })

            with open(self.produced_videos_path, 'w') as f:
                json.dump({"videos": produced}, f, indent=2)

        except Exception as e:
            print(f"   ⚠️  Could not mark topic as produced: {e}")

    def _get_default_profile(self) -> Dict[str, Any]:
        """Default channel profile when analysis not available"""
        return {
            "niche": "general",
            "sub_topics": [],
            "tone": "engaging",
            "avg_duration": 60,
            "hook_patterns": ["How to", "Why", "Best"],
            "target_audience": "general",
            "unique_angle": "informative and entertaining"
        }

    def _generate_fallback_trending(self, niche: str) -> List[Dict]:
        """Generate fallback trending topics when API unavailable"""
        fallback_topics = [
            f"Latest trends in {niche}",
            f"What's new in {niche} this month",
            f"{niche} news you need to know",
            f"Viral {niche} moments",
            f"Breaking {niche} updates"
        ]

        return [
            {
                "topic": topic,
                "snippet": f"Trending topic in {niche}",
                "source_url": "",
                "type": "trending",
                "discovered_at": datetime.now().isoformat()
            }
            for topic in fallback_topics
        ]
