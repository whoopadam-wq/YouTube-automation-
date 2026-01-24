"""
Tool Configuration Loader
Loads media generation tool preferences from saved configuration
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


class ToolConfigLoader:
    """Loads and manages tool configuration for media generation agents"""

    def __init__(self, config_path: str = "data/tool_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, List[str]]:
        """Load tool configuration from disk"""
        if not self.config_path.exists():
            print(f"ℹ️  No tool config found at {self.config_path}, using defaults")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                print(f"✅ Loaded tool configuration from {self.config_path}")
                return config
        except Exception as e:
            print(f"⚠️  Failed to load tool config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, List[str]]:
        """Default tool configuration"""
        return {
            "ideas-scraper": [],  # Text only - uses Claude + Serper (locked)
            "analytics": [],      # Text only - uses Claude (locked)
            "script": [],         # Text only - uses Claude + Serper (locked)
            "character": [],      # Text only - uses Claude (locked)
            "lighting": [],       # Text only - uses Claude (locked)
            "composition": [],    # Text only - uses Claude (locked)
            "frame": ["nano-banana-pro"],  # Image generation
            "video": ["veo-3", "elevenlabs"],  # Video + audio generation
            "assembly": ["remotion"]  # Video assembly
        }

    def get_tools_for_agent(self, agent_name: str) -> List[str]:
        """
        Get configured tools for a specific agent

        Args:
            agent_name: Name of the agent (e.g., "frame", "video", "assembly")

        Returns:
            List of tool IDs configured for this agent
        """
        return self.config.get(agent_name, [])

    def has_tool(self, agent_name: str, tool_id: str) -> bool:
        """
        Check if an agent has a specific tool configured

        Args:
            agent_name: Name of the agent
            tool_id: Tool identifier

        Returns:
            True if the tool is configured for this agent
        """
        return tool_id in self.get_tools_for_agent(agent_name)

    def get_primary_tool(self, agent_name: str) -> Optional[str]:
        """
        Get the primary (first) tool configured for an agent

        Args:
            agent_name: Name of the agent

        Returns:
            Tool ID or None if no tools configured
        """
        tools = self.get_tools_for_agent(agent_name)
        return tools[0] if tools else None

    def reload(self):
        """Reload configuration from disk"""
        self.config = self._load_config()

    def print_config(self):
        """Print current tool configuration"""
        print("\n" + "=" * 60)
        print("MEDIA TOOL CONFIGURATION")
        print("=" * 60)
        print("NOTE: Text agents always use Claude + Serper (not shown)\n")

        for agent, tools in self.config.items():
            # Only show media agents
            if agent in ["frame", "video", "assembly"]:
                if tools:
                    print(f"  {agent.upper()}: {', '.join(tools)}")
                else:
                    print(f"  {agent.upper()}: (not configured)")

        print("=" * 60 + "\n")


# Global instance
_tool_config = None


def get_tool_config() -> ToolConfigLoader:
    """Get the global tool configuration instance"""
    global _tool_config
    if _tool_config is None:
        _tool_config = ToolConfigLoader()
    return _tool_config
