#!/usr/bin/env python3
"""
Prompt Viewer - View and manage agent prompts
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from studio.config import get_prompt_manager
import yaml


def print_separator():
    print("=" * 80)


def view_all_prompts():
    """Display all agent prompts"""
    pm = get_prompt_manager()

    print_separator()
    print("AGENT PROMPT CONFIGURATION")
    print_separator()
    print(f"Config file: {pm.config_path}")
    print(f"Total agents configured: {len(pm.list_all_agents())}")
    print_separator()

    for agent_name in pm.list_all_agents():
        if agent_name == 'cinematic_compiler':
            print(f"\n🎬 CINEMATIC COMPILER AGENTS")
            compiler = pm.prompts.get('cinematic_compiler', {})
            for sub_agent, config in compiler.items():
                print(f"\n  └─ {sub_agent}")
                system_prompt = config.get('system_prompt', 'N/A')
                preview = system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt
                print(f"     {preview}")
        else:
            print(f"\n🤖 {agent_name.upper().replace('_', ' ')}")

            # System prompt
            system_prompt = pm.get_system_prompt(agent_name)
            if system_prompt:
                print(f"\n  System Prompt:")
                preview = system_prompt.strip()[:150] + "..." if len(system_prompt) > 150 else system_prompt.strip()
                print(f"  {preview}")

            # User prompt template
            user_template = pm.get_user_prompt_template(agent_name)
            if user_template:
                print(f"\n  User Prompt Template:")
                preview = user_template.strip()[:150] + "..." if len(user_template) > 150 else user_template.strip()
                print(f"  {preview}")

            # Audio config
            if agent_name == 'audio_agent':
                audio_config = pm.get_audio_config()
                if audio_config:
                    print(f"\n  Audio Configuration:")
                    for key, value in audio_config.items():
                        if key not in ['system_prompt', 'user_prompt_template']:
                            print(f"    {key}: {value}")

    print_separator()


def view_specific_agent(agent_name: str):
    """Display prompts for a specific agent"""
    pm = get_prompt_manager()

    if agent_name not in pm.list_all_agents():
        print(f"❌ Agent '{agent_name}' not found!")
        print(f"Available agents: {', '.join(pm.list_all_agents())}")
        return

    print_separator()
    print(f"PROMPTS FOR: {agent_name.upper().replace('_', ' ')}")
    print_separator()

    agent_config = pm.prompts.get(agent_name, {})

    for key, value in agent_config.items():
        print(f"\n{key}:")
        print("-" * 40)
        print(value)

    print_separator()


def export_prompts(output_file: str):
    """Export prompts to a new file"""
    pm = get_prompt_manager()
    pm.export_prompts(output_file)
    print(f"✅ Prompts exported to: {output_file}")


def list_agents():
    """List all configured agents"""
    pm = get_prompt_manager()

    print_separator()
    print("CONFIGURED AGENTS")
    print_separator()

    for i, agent_name in enumerate(pm.list_all_agents(), 1):
        print(f"{i}. {agent_name}")

    print_separator()
    print(f"Total: {len(pm.list_all_agents())} agents")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - show all prompts
        view_all_prompts()

    elif sys.argv[1] == "list":
        # List agents only
        list_agents()

    elif sys.argv[1] == "view" and len(sys.argv) == 3:
        # View specific agent
        view_specific_agent(sys.argv[2])

    elif sys.argv[1] == "export" and len(sys.argv) == 3:
        # Export to file
        export_prompts(sys.argv[2])

    elif sys.argv[1] == "edit":
        # Open config file in editor
        pm = get_prompt_manager()
        editor = os.environ.get('EDITOR', 'nano')
        os.system(f"{editor} {pm.config_path}")

    elif sys.argv[1] in ["-h", "--help", "help"]:
        print("""
Usage:
  python view_prompts.py              # View all prompts (summary)
  python view_prompts.py list         # List all agents
  python view_prompts.py view <agent> # View specific agent prompts
  python view_prompts.py export <file># Export prompts to file
  python view_prompts.py edit         # Edit prompts in $EDITOR

Examples:
  python view_prompts.py view lighting_agent
  python view_prompts.py export my_prompts.yaml
  python view_prompts.py edit
        """)

    else:
        print("❌ Invalid command")
        print("Run: python view_prompts.py --help")
