"""
Configuration Manager
Loads, validates, and provides access to all system configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class ChannelCharacterConfig(BaseModel):
    """Channel character (narrator) configuration."""
    name: str
    visual_description: str
    personality: str
    voice_style: str
    appearance_frequency: str = "intro_outro"


class UploadSchedule(BaseModel):
    """Upload schedule configuration."""
    time: str
    days: List[str]


class ChannelConfig(BaseModel):
    """Single channel configuration."""
    channel_id: str
    channel_name: str
    youtube_channel_id: str

    # Content
    niche: str
    topic: str
    base_prompt: str
    tone_style_modifiers: List[str]
    pacing_style: str
    visual_style: str

    # Channel character
    use_channel_character: bool = False
    channel_character: Optional[ChannelCharacterConfig] = None

    # Production
    long_form_enabled: bool = True
    shorts_enabled: bool = True
    shorts_per_day: int = 3
    target_long_duration: int = 10

    # Scheduling
    upload_timezone: str = "UTC"
    upload_schedule_long: List[UploadSchedule] = []
    upload_schedule_shorts: List[UploadSchedule] = []

    # Cost
    api_cost_cap_per_day: float = 15.0

    # Status
    status: str = "active"

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed = ['active', 'paused', 'testing']
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v

    @validator('pacing_style')
    def validate_pacing(cls, v):
        """Validate pacing style."""
        allowed = ['cinematic', 'fast', 'documentary', 'casual']
        if v not in allowed:
            raise ValueError(f"Pacing style must be one of: {allowed}")
        return v

    @validator('visual_style')
    def validate_visual(cls, v):
        """Validate visual style."""
        allowed = ['gritty', 'clean', 'dramatic', 'minimal', 'vibrant']
        if v not in allowed:
            raise ValueError(f"Visual style must be one of: {allowed}")
        return v


class ConfigManager:
    """
    Central configuration management system.
    Singleton pattern - one instance manages all configs.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize configuration manager."""
        if self._initialized:
            return

        # Load environment variables
        load_dotenv()

        # Set base paths
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / "config"
        self.data_path = self.base_path / "data"

        # Load configurations
        self.channels: List[ChannelConfig] = []
        self.system_config: Dict[str, Any] = {}
        self.api_providers: Dict[str, Any] = {}

        self._load_all_configs()
        self._initialized = True

    def _load_all_configs(self):
        """Load all configuration files."""
        # Load channels
        channels_file = self.config_path / "channels.yaml"
        if channels_file.exists():
            with open(channels_file, 'r') as f:
                channels_data = yaml.safe_load(f)
                for channel_data in channels_data.get('channels', []):
                    try:
                        channel = ChannelConfig(**channel_data)
                        self.channels.append(channel)
                    except Exception as e:
                        print(f"Error loading channel {channel_data.get('channel_id')}: {e}")

        # Load system config
        system_file = self.config_path / "system_config.yaml"
        if system_file.exists():
            with open(system_file, 'r') as f:
                self.system_config = yaml.safe_load(f)

        # Load API providers
        providers_file = self.config_path / "api_providers.yaml"
        if providers_file.exists():
            with open(providers_file, 'r') as f:
                self.api_providers = yaml.safe_load(f)

    def get_channel(self, channel_id: str) -> Optional[ChannelConfig]:
        """Get channel configuration by ID."""
        for channel in self.channels:
            if channel.channel_id == channel_id:
                return channel
        return None

    def get_active_channels(self) -> List[ChannelConfig]:
        """Get all active channels."""
        return [ch for ch in self.channels if ch.status == 'active']

    def get_system_setting(self, key: str, default: Any = None) -> Any:
        """Get system configuration setting."""
        keys = key.split('.')
        value = self.system_config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def get_provider_config(self, task: str) -> Dict[str, Any]:
        """Get provider configuration for a specific task."""
        providers = self.api_providers.get('providers', {})
        return providers.get(task, {})

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider from environment."""
        key_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'replicate': 'REPLICATE_API_TOKEN',
            'elevenlabs': 'ELEVENLABS_API_KEY',
            'runway': 'RUNWAY_API_KEY',
        }
        env_var = key_map.get(provider.lower())
        if env_var:
            return os.getenv(env_var)
        return None

    def reload_configs(self):
        """Reload all configurations from disk."""
        self.channels = []
        self.system_config = {}
        self.api_providers = {}
        self._load_all_configs()

    def validate_channel(self, channel_id: str) -> tuple[bool, str]:
        """Validate a channel configuration."""
        channel = self.get_channel(channel_id)
        if not channel:
            return False, f"Channel {channel_id} not found"

        # Check required API keys
        script_provider = self.get_provider_config('script_generation').get('primary')
        if not self.get_api_key(script_provider):
            return False, f"Missing API key for {script_provider}"

        # Check character config
        if channel.use_channel_character and not channel.channel_character:
            return False, "Channel character enabled but not configured"

        # Check schedules
        if channel.long_form_enabled and not channel.upload_schedule_long:
            return False, "Long-form enabled but no upload schedule set"

        if channel.shorts_enabled and not channel.upload_schedule_shorts:
            return False, "Shorts enabled but no upload schedule set"

        return True, "Channel configuration valid"

    def get_cost_estimates(self) -> Dict[str, Any]:
        """Get cost estimates from config."""
        return self.api_providers.get('cost_estimates', {})

    def get_rate_limits(self) -> Dict[str, int]:
        """Get rate limits from config."""
        return self.api_providers.get('rate_limits', {})

    def __repr__(self):
        """String representation."""
        return f"<ConfigManager: {len(self.channels)} channels, {len(self.get_active_channels())} active>"


# Global instance
config_manager = ConfigManager()
