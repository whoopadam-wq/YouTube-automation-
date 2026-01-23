"""
YouTube Channel Integration - Channel-aware automation system
Paste a channel URL and the entire system becomes channel-aware
"""
import os
import re
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from studio.agents.ideas_scraper_agent import IdeasScraperAgent
from studio.agents.analytics_agent import AnalyticsAgent


class ChannelProfile:
    """Represents a YouTube channel profile"""
    def __init__(
        self,
        channel_id: str,
        channel_name: str,
        subscriber_count: int,
        video_count: int,
        niche: str,
        tone: str,
        avg_duration: float,
        target_audience: str,
        upload_frequency: str,
        top_topics: list,
        style_notes: str
    ):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.subscriber_count = subscriber_count
        self.video_count = video_count
        self.niche = niche
        self.tone = tone
        self.avg_duration = avg_duration
        self.target_audience = target_audience
        self.upload_frequency = upload_frequency
        self.top_topics = top_topics
        self.style_notes = style_notes
        self.loaded_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "subscriber_count": self.subscriber_count,
            "video_count": self.video_count,
            "niche": self.niche,
            "tone": self.tone,
            "avg_duration_seconds": self.avg_duration,
            "target_audience": self.target_audience,
            "upload_frequency": self.upload_frequency,
            "top_topics": self.top_topics,
            "style_notes": self.style_notes,
            "loaded_at": self.loaded_at
        }


class YouTubeChannelIntegration:
    """
    Channel integration system that:
    - Accepts YouTube channel URL or ID
    - Extracts channel information via YouTube API
    - Analyzes channel style, tone, and content patterns
    - Creates channel profile for all agents to use
    - Automatically starts Ideas Scraper for channel
    - Runs Analytics Agent to learn from channel
    - Makes entire system "channel-aware"
    - Stores channel context for future productions
    - Seamlessly integrates with production pipeline
    """

    def __init__(self):
        self.youtube_api_key = os.environ.get('YOUTUBE_DATA_API_KEY')

        # Storage
        self.channels_db_path = "data/channels.json"
        self.active_channel_path = "data/active_channel.json"

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Agents for channel analysis
        self.ideas_agent = None
        self.analytics_agent = None

    async def integrate_channel(
        self,
        channel_input: str,
        auto_analyze: bool = True,
        auto_discover_ideas: bool = True
    ) -> ChannelProfile:
        """
        Main method: Integrate a YouTube channel

        Args:
            channel_input: Channel URL or channel ID
            auto_analyze: Automatically run analytics
            auto_discover_ideas: Automatically discover video ideas

        Returns:
            ChannelProfile with all channel information
        """
        print(f"🔗 Channel Integration: Connecting to channel...")

        # Step 1: Extract channel ID from input
        try:
            channel_id = self._extract_channel_id(channel_input)
        except Exception as e:
            # If _extract_channel_id raises an error, pass it through
            raise

        if not channel_id:
            raise ValueError(
                f"Could not extract channel ID from: {channel_input}\n\n"
                f"Supported formats:\n"
                f"• https://www.youtube.com/@YourChannel\n"
                f"• https://www.youtube.com/channel/UCxxxxxxxx\n"
                f"• https://www.youtube.com/c/YourChannel\n"
                f"• UCxxxxxxxx (direct channel ID)\n\n"
                f"Make sure the URL is complete and correct."
            )

        print(f"   📌 Channel ID: {channel_id}")

        # Step 2: Fetch channel info from YouTube
        print(f"   📥 Fetching channel information...")
        channel_data = await self._fetch_channel_info(channel_id)

        # Step 3: Analyze channel style and content
        print(f"   🔍 Analyzing channel style...")
        channel_profile = await self._create_channel_profile(channel_id, channel_data)

        # Step 4: Save as active channel
        self._save_active_channel(channel_profile)

        # Step 5: Run analytics if requested
        if auto_analyze:
            print(f"   📊 Running analytics analysis...")
            try:
                await self._run_initial_analytics(channel_id)
            except Exception as e:
                print(f"   ⚠️  Analytics failed: {e}")
                print(f"   ℹ️  You can run analytics later from the dashboard")

        # Step 6: Discover video ideas if requested
        if auto_discover_ideas:
            print(f"   💡 Discovering video ideas...")
            try:
                await self._discover_initial_ideas(channel_profile)
            except Exception as e:
                print(f"   ⚠️  Ideas discovery failed: {e}")
                print(f"   ℹ️  You can discover ideas later from the dashboard")

        print(f"✅ Channel Integration: '{channel_profile.channel_name}' is now connected")
        print(f"   📺 {channel_profile.subscriber_count:,} subscribers")
        print(f"   🎥 {channel_profile.video_count} videos")
        print(f"   🎯 Niche: {channel_profile.niche}")

        return channel_profile

    def _extract_channel_id(self, channel_input: str) -> Optional[str]:
        """
        Extract channel ID from various input formats:
        - https://www.youtube.com/channel/UCxxxxx
        - https://www.youtube.com/@username
        - UCxxxxx (direct channel ID)
        - youtube.com/@username/UCxxxxx (user providing ID directly)
        """
        # First, look for any UC channel ID pattern anywhere in the input
        # This handles cases like: youtube.com/@username/UCh27s70sw2lhLHqmJ72z__A
        uc_pattern = re.search(r'\b(UC[a-zA-Z0-9_-]{22})\b', channel_input)
        if uc_pattern:
            channel_id = uc_pattern.group(1)
            print(f"   📌 Extracted Channel ID directly: {channel_id}")
            return channel_id

        # Direct channel ID format (clean input)
        if channel_input.startswith('UC') and len(channel_input) == 24:
            return channel_input

        # URL format: /channel/UCxxxxx
        channel_match = re.search(r'/channel/([UC][a-zA-Z0-9_-]{22,})', channel_input)
        if channel_match:
            return channel_match.group(1)

        # URL format: /@username (need to resolve via API)
        username_match = re.search(r'/@([a-zA-Z0-9_-]+)', channel_input)
        if username_match:
            username = username_match.group(1)
            print(f"   🔍 Resolving @{username} to Channel ID...")
            return self._resolve_username_to_channel_id(username)

        # Custom URL format: /c/channelname
        custom_match = re.search(r'/c/([a-zA-Z0-9_-]+)', channel_input)
        if custom_match:
            custom_name = custom_match.group(1)
            return self._resolve_custom_url_to_channel_id(custom_name)

        return None

    def _resolve_username_to_channel_id(self, username: str) -> Optional[str]:
        """Resolve @username to channel ID using YouTube API"""
        if not self.youtube_api_key:
            raise ValueError("YouTube API key is required to resolve username to channel ID")

        # Method 1: Try forHandle (for new @handle format)
        try:
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "id",
                "forHandle": username,
                "key": self.youtube_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                print(f"   ✅ Resolved @{username} via forHandle")
                return data["items"][0]["id"]

        except Exception as e:
            print(f"   ⚠️  forHandle method failed: {e}")

        # Method 2: Try forUsername (for legacy usernames)
        try:
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "id",
                "forUsername": username,
                "key": self.youtube_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                print(f"   ✅ Resolved @{username} via forUsername")
                return data["items"][0]["id"]

        except Exception as e:
            print(f"   ⚠️  forUsername method failed: {e}")

        # Method 3: Try search API as last resort
        try:
            url = f"https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": username,
                "type": "channel",
                "maxResults": 1,
                "key": self.youtube_api_key
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                channel_id = data["items"][0]["snippet"]["channelId"]
                print(f"   ✅ Resolved @{username} via search")
                return channel_id

        except Exception as e:
            print(f"   ⚠️  Search method failed: {e}")

        raise ValueError(
            f"Could not resolve @{username} to a channel ID.\n\n"
            f"This could mean:\n"
            f"1. The channel doesn't exist or was deleted\n"
            f"2. The handle/username is incorrect\n"
            f"3. The channel is private\n\n"
            f"Try using the direct channel URL format instead:\n"
            f"https://www.youtube.com/channel/UCxxxxxxxx"
        )

    def _resolve_custom_url_to_channel_id(self, custom_name: str) -> Optional[str]:
        """Resolve custom URL to channel ID"""
        # Similar to username resolution
        return self._resolve_username_to_channel_id(custom_name)

    async def _fetch_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Fetch channel information from YouTube Data API"""
        if not self.youtube_api_key:
            raise ValueError(
                "YOUTUBE_DATA_API_KEY is required for channel integration.\n\n"
                "Get your free API key:\n"
                "1. Go to https://console.cloud.google.com/apis/credentials\n"
                "2. Create a new project (or select existing)\n"
                "3. Enable 'YouTube Data API v3'\n"
                "4. Create credentials > API key\n"
                "5. Add to Render: Environment > YOUTUBE_DATA_API_KEY\n\n"
                "Without this key, the system cannot access real YouTube data."
            )

        try:
            url = f"https://www.googleapis.com/youtube/v3/channels"
            params = {
                "part": "snippet,statistics,brandingSettings,contentDetails",
                "id": channel_id,
                "key": self.youtube_api_key
            }

            print(f"   📡 Calling YouTube API for channel: {channel_id}")
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # Check for API errors
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown API error")
                raise ValueError(f"YouTube API Error: {error_msg}")

            if "items" not in data or len(data["items"]) == 0:
                raise ValueError(
                    f"Channel {channel_id} not found.\n\n"
                    f"This could mean:\n"
                    f"1. The Channel ID is incorrect\n"
                    f"2. The channel is private or deleted\n"
                    f"3. The channel was suspended\n\n"
                    f"Please verify the Channel ID is correct.\n"
                    f"You can find your Channel ID in YouTube Studio > Settings > Channel > Advanced settings"
                )

            channel_item = data["items"][0]

            channel_info = {
                "id": channel_id,
                "title": channel_item["snippet"]["title"],
                "description": channel_item["snippet"]["description"],
                "subscriber_count": int(channel_item["statistics"].get("subscriberCount", 0)),
                "video_count": int(channel_item["statistics"].get("videoCount", 0)),
                "view_count": int(channel_item["statistics"].get("viewCount", 0)),
                "thumbnail": channel_item["snippet"]["thumbnails"]["high"]["url"],
                "country": channel_item["snippet"].get("country", "Unknown"),
                "custom_url": channel_item["snippet"].get("customUrl", "")
            }

            print(f"   ✅ Found channel: {channel_info['title']}")
            print(f"   📊 {channel_info['subscriber_count']:,} subscribers, {channel_info['video_count']} videos")

            return channel_info

        except requests.exceptions.RequestException as e:
            raise ValueError(
                f"Network error connecting to YouTube API: {e}\n\n"
                f"Please check your internet connection and try again."
            )
        except ValueError:
            # Re-raise ValueError as-is (these are our custom error messages)
            raise
        except Exception as e:
            raise ValueError(
                f"Unexpected error fetching channel info: {e}\n\n"
                f"Channel ID: {channel_id}\n"
                f"Please verify the Channel ID is correct."
            )

    async def _create_channel_profile(
        self,
        channel_id: str,
        channel_data: Dict[str, Any]
    ) -> ChannelProfile:
        """
        Create detailed channel profile by analyzing content
        ACTUALLY analyzes uploaded videos to determine niche
        """
        # Initialize default values
        niche = "general"
        tone = "engaging"
        top_topics = []
        avg_duration = 300
        style_notes = "Channel connected"

        # STEP 1: Fetch actual videos from the channel
        print(f"   📹 Fetching uploaded videos...")
        videos = await self._fetch_channel_videos_with_details(channel_id)

        if videos and len(videos) > 0:
            print(f"   ✅ Found {len(videos)} videos on channel")

            # STEP 2: Analyze the actual video content to determine niche
            print(f"   🧠 Analyzing video content to determine niche...")
            niche_analysis = await self._analyze_videos_for_niche(videos, channel_data)

            niche = niche_analysis.get('niche', 'general')
            tone = niche_analysis.get('tone', 'engaging')
            top_topics = niche_analysis.get('topics', [])

            # Calculate average duration from real videos
            if videos:
                total_duration = sum(v.get('duration_seconds', 0) for v in videos)
                avg_duration = int(total_duration / len(videos)) if len(videos) > 0 else 300

            style_notes = f"Analyzed {len(videos)} video(s) - Niche: {niche}"
            print(f"   ✅ Detected niche: {niche}")
        else:
            print(f"   ⚠️  No videos found - using basic profile")
            # Still try description analysis as fallback
            description = channel_data.get('description', '').lower()
            if description:
                if any(word in description for word in ['tech', 'technology', 'coding', 'programming']):
                    niche = "technology"
                elif any(word in description for word in ['gaming', 'games', 'gamer']):
                    niche = "gaming"
                elif any(word in description for word in ['cooking', 'recipe', 'food']):
                    niche = "cooking"
                elif any(word in description for word in ['fitness', 'workout', 'health']):
                    niche = "fitness"

        # Create profile
        profile = ChannelProfile(
            channel_id=channel_id,
            channel_name=channel_data.get('title', 'Unknown Channel'),
            subscriber_count=channel_data.get('subscriber_count', 0),
            video_count=channel_data.get('video_count', 0),
            niche=niche,
            tone=tone,
            avg_duration=avg_duration,
            target_audience="general",
            upload_frequency="regular",
            top_topics=top_topics if top_topics else [niche],
            style_notes=style_notes
        )

        return profile

    async def _fetch_channel_videos_with_details(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Fetch actual videos from the channel with full details
        Gets title, description, transcript (if available)
        """
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
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist,
                "maxResults": 10,  # Get up to 10 most recent videos
                "key": self.youtube_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            playlist_data = response.json()

            videos = []
            for item in playlist_data.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]

                # Get video details including duration
                video_url = f"https://www.googleapis.com/youtube/v3/videos"
                video_params = {
                    "part": "snippet,contentDetails,statistics",
                    "id": video_id,
                    "key": self.youtube_api_key
                }
                video_response = requests.get(video_url, params=video_params, timeout=10)
                video_data = video_response.json()

                if "items" in video_data and len(video_data["items"]) > 0:
                    video_item = video_data["items"][0]

                    # Parse ISO 8601 duration
                    duration_str = video_item["contentDetails"]["duration"]
                    duration_seconds = self._parse_duration(duration_str)

                    videos.append({
                        "video_id": video_id,
                        "title": video_item["snippet"]["title"],
                        "description": video_item["snippet"]["description"],
                        "duration_seconds": duration_seconds,
                        "views": int(video_item["statistics"].get("viewCount", 0)),
                        "likes": int(video_item["statistics"].get("likeCount", 0)),
                        "published_at": video_item["snippet"]["publishedAt"]
                    })

            return videos

        except Exception as e:
            print(f"   ⚠️  Error fetching videos: {e}")
            return []

    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    async def _analyze_videos_for_niche(
        self,
        videos: List[Dict[str, Any]],
        channel_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Claude to analyze actual video content and determine the channel niche
        This is the REAL analysis using actual video data
        """
        if not videos:
            return {"niche": "general", "tone": "engaging", "topics": []}

        # Check if we have Anthropic API key
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not anthropic_key:
            print(f"   ⚠️  ANTHROPIC_API_KEY not set - using basic niche detection")
            return {"niche": "general", "tone": "engaging", "topics": []}

        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=anthropic_key)

            # Prepare video content for analysis
            video_summaries = []
            for video in videos[:5]:  # Analyze up to 5 most recent videos
                video_summaries.append(
                    f"Title: {video['title']}\n"
                    f"Description: {video['description'][:200]}...\n"
                    f"Duration: {video['duration_seconds']}s\n"
                    f"Views: {video['views']}\n"
                )

            channel_description = channel_data.get('description', '')
            channel_name = channel_data.get('title', '')

            prompt = f"""Analyze this YouTube channel's content and determine the EXACT niche.

Channel Name: {channel_name}
Channel Description: {channel_description}

Recent Videos:
{chr(10).join(video_summaries)}

Based on the video titles, descriptions, and channel info, determine:
1. The SPECIFIC niche (be precise - don't say "general", identify the actual topic)
2. The tone/style (educational, entertaining, professional, casual, etc.)
3. Top 3 topics this channel covers

Return JSON:
{{
    "niche": "specific niche here (e.g., 'survival skills', 'primitive technology', 'DIY crafts', 'science experiments', etc.)",
    "tone": "tone here",
    "topics": ["topic1", "topic2", "topic3"]
}}

Be SPECIFIC about the niche. Examples of good niches:
- "primitive technology and survival skills"
- "DIY home improvement"
- "science experiments and education"
- "cooking and recipes"
- "gaming walkthroughs"
- "fitness and workout routines"

DO NOT say "general" - identify the actual content focus."""

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Extract JSON
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                analysis = json.loads(response_text[start_idx:end_idx])
                return analysis

        except Exception as e:
            print(f"   ⚠️  Claude analysis failed: {e}")

        return {"niche": "general", "tone": "engaging", "topics": []}

    async def _run_initial_analytics(self, channel_id: str):
        """Run initial analytics to learn from channel"""
        if not self.analytics_agent:
            self.analytics_agent = AnalyticsAgent(channel_id=channel_id)

        # Run comprehensive analysis
        await self.analytics_agent.analyze_channel_performance(days_back=90, min_videos=3)

        print(f"   ✅ Analytics complete - learnings saved")

    async def _discover_initial_ideas(self, channel_profile: ChannelProfile):
        """Discover initial video ideas for the channel"""
        self.ideas_agent = IdeasScraperAgent(channel_id=channel_profile.channel_id)

        # Discover ideas based on channel niche
        ideas = await self.ideas_agent.discover_ideas(
            niche=channel_profile.niche,
            num_ideas=10,
            include_trending=True,
            include_evergreen=True
        )

        print(f"   ✅ Discovered {len(ideas)} video ideas")

    def _save_active_channel(self, profile: ChannelProfile):
        """Save as the active channel for production"""
        try:
            with open(self.active_channel_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)

            # Also add to channels database
            channels = []
            if os.path.exists(self.channels_db_path):
                with open(self.channels_db_path, 'r') as f:
                    data = json.load(f)
                    channels = data.get('channels', [])

            # Update or add channel
            channel_exists = False
            for i, ch in enumerate(channels):
                if ch.get('channel_id') == profile.channel_id:
                    channels[i] = profile.to_dict()
                    channel_exists = True
                    break

            if not channel_exists:
                channels.append(profile.to_dict())

            with open(self.channels_db_path, 'w') as f:
                json.dump({"channels": channels}, f, indent=2)

            print(f"   💾 Channel profile saved")

        except Exception as e:
            print(f"   ⚠️  Could not save channel profile: {e}")

    def load_active_channel(self) -> Optional[ChannelProfile]:
        """Load the currently active channel"""
        try:
            if os.path.exists(self.active_channel_path):
                with open(self.active_channel_path, 'r') as f:
                    data = json.load(f)

                return ChannelProfile(
                    channel_id=data['channel_id'],
                    channel_name=data['channel_name'],
                    subscriber_count=data['subscriber_count'],
                    video_count=data['video_count'],
                    niche=data['niche'],
                    tone=data['tone'],
                    avg_duration=data['avg_duration_seconds'],
                    target_audience=data['target_audience'],
                    upload_frequency=data['upload_frequency'],
                    top_topics=data['top_topics'],
                    style_notes=data['style_notes']
                )

        except Exception as e:
            print(f"⚠️  Could not load active channel: {e}")

        return None

    def list_integrated_channels(self) -> list:
        """List all integrated channels"""
        try:
            if os.path.exists(self.channels_db_path):
                with open(self.channels_db_path, 'r') as f:
                    data = json.load(f)
                    return data.get('channels', [])
        except Exception as e:
            print(f"⚠️  Could not load channels: {e}")

        return []



# Convenience function
async def quick_integrate(channel_url: str) -> ChannelProfile:
    """Quick channel integration"""
    integration = YouTubeChannelIntegration()
    return await integration.integrate_channel(channel_url)
