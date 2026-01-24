"""
Prompt Manager - Centralized prompt configuration for all agents
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """
    Manages all agent prompts from a central configuration file.
    Allows runtime prompt loading and customization.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize prompt manager

        Args:
            config_path: Path to agent_prompts.yaml (defaults to studio/config/agent_prompts.yaml)
        """
        if config_path is None:
            # Default to studio/config/agent_prompts.yaml
            config_path = Path(__file__).parent / "agent_prompts.yaml"

        self.config_path = config_path
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML file"""
        if not os.path.exists(self.config_path):
            print(f"⚠️  Warning: Prompt config not found at {self.config_path}")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                prompts = yaml.safe_load(f)
            print(f"✅ Loaded prompts from {self.config_path}")
            return prompts or {}
        except Exception as e:
            print(f"❌ Failed to load prompts: {e}")
            return {}

    def reload(self):
        """Reload prompts from file (useful for hot-reloading)"""
        self.prompts = self._load_prompts()

    def get(self, agent_name: str, key: str, default: Any = None) -> Any:
        """
        Get a prompt value for a specific agent

        Args:
            agent_name: Name of the agent (e.g., 'script_agent', 'lighting_agent')
            key: Key within the agent config (e.g., 'system_prompt', 'user_prompt_template')
            default: Default value if not found

        Returns:
            Prompt value or default
        """
        return self.prompts.get(agent_name, {}).get(key, default)

    def format_prompt(
        self,
        agent_name: str,
        template_key: str,
        **kwargs
    ) -> str:
        """
        Format a prompt template with variables

        Args:
            agent_name: Name of the agent
            template_key: Key for the template (e.g., 'user_prompt_template')
            **kwargs: Variables to substitute into the template

        Returns:
            Formatted prompt string
        """
        template = self.get(agent_name, template_key, "")
        if not template:
            return ""

        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"⚠️  Missing variable in prompt template: {e}")
            return template

    def get_system_prompt(self, agent_name: str) -> str:
        """Get system prompt for an agent"""
        return self.get(agent_name, 'system_prompt', '')

    def get_user_prompt_template(self, agent_name: str) -> str:
        """Get user prompt template for an agent"""
        return self.get(agent_name, 'user_prompt_template', '')

    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio agent configuration"""
        return self.prompts.get('audio_agent', {})

    def get_video_prompt_template(self) -> str:
        """Get video agent prompt template"""
        return self.get('video_agent', 'prompt_template', '')

    def get_cinematic_compiler_prompt(self, agent_name: str) -> str:
        """Get cinematic compiler agent prompt"""
        compiler_prompts = self.prompts.get('cinematic_compiler', {})
        return compiler_prompts.get(agent_name, {}).get('system_prompt', '')

    def list_all_agents(self) -> list:
        """List all configured agents"""
        return list(self.prompts.keys())

    def export_prompts(self, output_path: str):
        """Export current prompts to a file"""
        with open(output_path, 'w') as f:
            yaml.dump(self.prompts, f, default_flow_style=False, sort_keys=False)
        print(f"✅ Exported prompts to {output_path}")

    def __repr__(self):
        agent_count = len(self.list_all_agents())
        return f"<PromptManager: {agent_count} agents configured>"


# Global instance for easy import
_global_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """Get or create global prompt manager instance"""
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager()
    return _global_prompt_manager


# Convenience functions
def get_system_prompt(agent_name: str) -> str:
    """Get system prompt for an agent"""
    return get_prompt_manager().get_system_prompt(agent_name)


def format_user_prompt(agent_name: str, **kwargs) -> str:
    """Format user prompt template with variables"""
    return get_prompt_manager().format_prompt(agent_name, 'user_prompt_template', **kwargs)


def reload_prompts():
    """Reload prompts from file"""
    get_prompt_manager().reload()
