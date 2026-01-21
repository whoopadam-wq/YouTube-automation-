"""
State Manager
Tracks the state of all content generation across channels and videos.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum


class ContentStatus(Enum):
    """Content generation status."""
    QUEUED = "queued"
    SCRIPT_GENERATION = "script_generation"
    CHARACTER_CREATION = "character_creation"
    SCENE_PLANNING = "scene_planning"
    MEDIA_GENERATION = "media_generation"
    ASSEMBLY = "assembly"
    UPLOAD_PENDING = "upload_pending"
    UPLOADED = "uploaded"
    FAILED = "failed"


class StateManager:
    """
    Manages state of content generation pipeline.
    Uses SQLite for persistence.
    """

    def __init__(self, config_manager):
        """Initialize state manager."""
        self.config = config_manager
        self.db_path = config_manager.data_path / "database" / "automation.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                channel_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_upload_time TIMESTAMP,
                uploaded_at TIMESTAMP,
                youtube_video_id TEXT,
                title TEXT,
                description TEXT,
                error_message TEXT,
                metadata TEXT
            )
        """)

        # Pipeline stages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_stages (
                stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                stage_name TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                output_data TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        """)

        # Assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                asset_id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                file_path TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stages_video ON pipeline_stages(video_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_video ON assets(video_id)")

        conn.commit()
        conn.close()

    def create_video(
        self,
        video_id: str,
        channel_id: str,
        content_type: str,
        scheduled_upload_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new video entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO videos (
                video_id, channel_id, content_type, status,
                scheduled_upload_time, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            channel_id,
            content_type,
            ContentStatus.QUEUED.value,
            scheduled_upload_time,
            json.dumps(metadata or {})
        ))

        conn.commit()
        conn.close()

        return video_id

    def update_video_status(
        self,
        video_id: str,
        status: ContentStatus,
        error_message: Optional[str] = None
    ):
        """Update video status."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE videos
            SET status = ?, updated_at = CURRENT_TIMESTAMP, error_message = ?
            WHERE video_id = ?
        """, (status.value, error_message, video_id))

        conn.commit()
        conn.close()

    def start_pipeline_stage(
        self,
        video_id: str,
        stage_name: str
    ) -> int:
        """Start a pipeline stage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pipeline_stages (
                video_id, stage_name, status, started_at
            ) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (video_id, stage_name, 'in_progress'))

        stage_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return stage_id

    def complete_pipeline_stage(
        self,
        stage_id: int,
        success: bool = True,
        error_message: Optional[str] = None,
        output_data: Optional[Dict[str, Any]] = None
    ):
        """Complete a pipeline stage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        status = 'completed' if success else 'failed'

        cursor.execute("""
            UPDATE pipeline_stages
            SET status = ?, completed_at = CURRENT_TIMESTAMP,
                error_message = ?, output_data = ?
            WHERE stage_id = ?
        """, (status, error_message, json.dumps(output_data or {}), stage_id))

        conn.commit()
        conn.close()

    def add_asset(
        self,
        asset_id: str,
        video_id: str,
        asset_type: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add an asset to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO assets (
                asset_id, video_id, asset_type, file_path, url, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (asset_id, video_id, asset_type, file_path, url, json.dumps(metadata or {})))

        conn.commit()
        conn.close()

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    def get_videos_by_channel(
        self,
        channel_id: str,
        status: Optional[ContentStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get videos for a channel."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if status:
            cursor.execute("""
                SELECT * FROM videos
                WHERE channel_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (channel_id, status.value, limit))
        else:
            cursor.execute("""
                SELECT * FROM videos
                WHERE channel_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (channel_id, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_pending_uploads(self) -> List[Dict[str, Any]]:
        """Get videos pending upload."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM videos
            WHERE status = ?
            AND scheduled_upload_time <= CURRENT_TIMESTAMP
            ORDER BY scheduled_upload_time ASC
        """, (ContentStatus.UPLOAD_PENDING.value,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def mark_uploaded(
        self,
        video_id: str,
        youtube_video_id: str
    ):
        """Mark video as uploaded."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE videos
            SET status = ?, uploaded_at = CURRENT_TIMESTAMP,
                youtube_video_id = ?
            WHERE video_id = ?
        """, (ContentStatus.UPLOADED.value, youtube_video_id, video_id))

        conn.commit()
        conn.close()

    def get_assets(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all assets for a video."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM assets
            WHERE video_id = ?
            ORDER BY created_at ASC
        """, (video_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_pipeline_stages(self, video_id: str) -> List[Dict[str, Any]]:
        """Get all pipeline stages for a video."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM pipeline_stages
            WHERE video_id = ?
            ORDER BY started_at ASC
        """, (video_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_stats(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if channel_id:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM videos
                WHERE channel_id = ?
                GROUP BY status
            """, (channel_id,))
        else:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM videos
                GROUP BY status
            """)

        rows = cursor.fetchall()
        conn.close()

        stats = {status: 0 for status in ContentStatus}
        for status, count in rows:
            stats[status] = count

        return stats

    def cleanup_old_records(self, days: int = 30):
        """Clean up old completed records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM videos
            WHERE status = ? AND uploaded_at < datetime('now', '-{} days')
        """.format(days), (ContentStatus.UPLOADED.value,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted
