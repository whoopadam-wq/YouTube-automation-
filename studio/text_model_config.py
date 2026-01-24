"""
Text Model Configuration - LOCKED TO CLAUDE + SERPER

⚠️ CRITICAL: DO NOT MODIFY THIS FILE ⚠️

All text generation in this system MUST use:
- Claude API (Anthropic) for reasoning and writing
- Serper API for internet access and research

This is NOT configurable. Media generation (image/video/audio) can use different
providers, but text is LOCKED to Claude + Serper.

All agents for:
- Idea generation
- Research
- Script writing
- Character extraction
- Scene planning
- Camera descriptions
- Composition / mood / pacing

MUST use Claude API.
"""

# Text model - LOCKED, DO NOT CHANGE
TEXT_MODEL = "claude-sonnet-4-5"

# Required APIs for text agents
REQUIRED_TEXT_APIS = {
    "claude": "ANTHROPIC_API_KEY",      # Required for ALL text agents
    "serper": "SERPER_API_KEY",         # Required for research (ideas, script)
    "youtube": "YOUTUBE_DATA_API_KEY"   # Optional for analytics
}


def get_text_model() -> str:
    """
    Get the locked text model ID.

    Returns:
        str: Always returns "claude-sonnet-4-5"
    """
    return TEXT_MODEL


def validate_text_apis() -> dict:
    """
    Validate that required text APIs are configured.

    Returns:
        dict: Status of each API
    """
    import os

    status = {}
    for name, env_var in REQUIRED_TEXT_APIS.items():
        api_key = os.environ.get(env_var)
        status[name] = {
            "configured": bool(api_key),
            "env_var": env_var,
            "required": name in ["claude", "serper"]
        }

    return status


def print_text_config_status():
    """Print the current text API configuration status."""
    print("=" * 60)
    print("TEXT MODEL CONFIGURATION (LOCKED)")
    print("=" * 60)
    print(f"Model: {TEXT_MODEL}")
    print("\nAPI Status:")

    status = validate_text_apis()
    for name, info in status.items():
        icon = "✅" if info["configured"] else "❌"
        required = "(REQUIRED)" if info["required"] else "(optional)"
        print(f"  {icon} {name.upper()}: {info['env_var']} {required}")

    print("=" * 60)
