"""
Unified Post Manager
Handles posting to multiple platforms
"""
from typing import List
from studio.schemas import ProductionJob
from studio.posting.youtube_poster import YouTubePoster
from studio.posting.tiktok_poster import TikTokPoster
from studio.posting.instagram_poster import InstagramPoster


class PostManager:
    """
    Unified manager for posting to all platforms
    """

    def __init__(self):
        self.youtube = YouTubePoster()
        self.tiktok = TikTokPoster()
        self.instagram = InstagramPoster()

    async def post_to_platforms(
        self,
        job: ProductionJob,
        platforms: List[str],
        youtube_privacy: str = "private",
        tiktok_privacy: str = "SELF_ONLY",
        instagram_share_to_feed: bool = True
    ) -> ProductionJob:
        """
        Post video to specified platforms

        Args:
            job: ProductionJob with final_video_path
            platforms: List of platforms ["youtube", "tiktok", "instagram"]
            youtube_privacy: YouTube privacy setting
            tiktok_privacy: TikTok privacy level
            instagram_share_to_feed: Share Instagram Reel to feed

        Returns:
            Updated ProductionJob with posting URLs
        """
        if not job.final_video_path:
            raise ValueError("Job has no final video")

        print(f"\n📤 Posting to platforms: {', '.join(platforms)}")

        # Post to YouTube
        if "youtube" in platforms:
            try:
                result = await self.youtube.upload_video(
                    video_path=job.final_video_path,
                    title=job.title,
                    description=self._generate_description(job),
                    tags=self._generate_tags(job),
                    privacy_status=youtube_privacy
                )
                job.posted_to_youtube = True
                job.youtube_url = result["video_url"]
                print(f"   ✅ YouTube: {result['video_url']}")
            except Exception as e:
                print(f"   ❌ YouTube failed: {e}")

        # Post to TikTok
        if "tiktok" in platforms:
            try:
                result = await self.tiktok.upload_video(
                    video_path=job.final_video_path,
                    caption=self._generate_caption(job, platform="tiktok"),
                    privacy_level=tiktok_privacy
                )
                job.posted_to_tiktok = True
                job.tiktok_url = result["share_url"]
                print(f"   ✅ TikTok: {result['share_url']}")
            except Exception as e:
                print(f"   ❌ TikTok failed: {e}")

        # Post to Instagram
        if "instagram" in platforms:
            try:
                # Instagram requires video to be hosted publicly
                # In production, upload to CDN first
                if not job.final_video_url:
                    print(f"   ⚠️  Instagram skipped: No public video URL")
                else:
                    result = await self.instagram.upload_reel(
                        video_url=job.final_video_url,
                        caption=self._generate_caption(job, platform="instagram"),
                        share_to_feed=instagram_share_to_feed
                    )
                    job.posted_to_instagram = True
                    job.instagram_url = result["permalink"]
                    print(f"   ✅ Instagram: {result['permalink']}")
            except Exception as e:
                print(f"   ❌ Instagram failed: {e}")

        print(f"\n✅ Posting complete")

        return job

    def _generate_description(self, job: ProductionJob) -> str:
        """Generate video description"""
        description = f"{job.title}\n\n"

        # Add scene summaries
        if job.clips:
            description += "Timeline:\n"
            for clip in job.clips[:5]:  # First 5 scenes
                description += f"• {clip.scene_description}\n"

        description += "\n---\n"
        description += f"Platform: {job.platform}\n"
        description += f"Style: {job.visual_style}\n"

        return description

    def _generate_tags(self, job: ProductionJob) -> List[str]:
        """Generate video tags"""
        tags = [
            job.platform,
            job.visual_style,
            "AI generated",
            "automated content"
        ]

        # Add character names
        for char in job.global_characters:
            tags.append(char.name.lower())

        return tags[:15]  # YouTube allows max 15 tags

    def _generate_caption(self, job: ProductionJob, platform: str) -> str:
        """Generate platform-specific caption"""
        if platform == "tiktok":
            # TikTok: Short, punchy, hashtag-heavy
            caption = f"{job.title} 🎬\n\n"
            caption += "#fyp #foryou #ai #viral"
            return caption[:2200]  # Max length

        elif platform == "instagram":
            # Instagram: Aesthetic, engaging
            caption = f"{job.title}\n\n"
            caption += f"{job.clips[0].narration_text if job.clips else ''}\n\n"
            caption += "#reels #ai #content"
            return caption[:2200]

        else:
            return job.title
