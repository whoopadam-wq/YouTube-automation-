#!/usr/bin/env python3
"""
AI Content Automation Dashboard
Beautiful web UI for managing the automation system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
from datetime import datetime, timedelta
import json

from core import ConfigManager, StateManager, CostTracker, AsyncOrchestrator
from modules import (
    ScriptGenerator, CharacterCreator, AnchorCharacterManager,
    ScenePlanner, MediaGenerator, VideoAssembler, ShortsGenerator, Scheduler
)
from workflows import LongFormWorkflow, ShortFormWorkflow

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')

# Initialize system components (these work without API keys)
config = ConfigManager()
state = StateManager(config)
cost_tracker = CostTracker(config)
orchestrator = AsyncOrchestrator(config)

# Check if API keys are configured
def has_api_keys():
    """Check if any API keys are configured."""
    keys = [
        os.environ.get('ANTHROPIC_API_KEY'),
        os.environ.get('OPENAI_API_KEY'),
        os.environ.get('REPLICATE_API_TOKEN'),
        os.environ.get('ELEVENLABS_API_KEY')
    ]
    return any(key for key in keys)

API_KEYS_CONFIGURED = has_api_keys()

# Initialize modules (only if API keys are present)
if API_KEYS_CONFIGURED:
    try:
        script_gen = ScriptGenerator(config, cost_tracker)
        char_creator = CharacterCreator(config, cost_tracker)
        anchor_mgr = AnchorCharacterManager(config, cost_tracker)
        scene_planner = ScenePlanner(config, cost_tracker)
        media_gen = MediaGenerator(config, cost_tracker, orchestrator)
        video_assembler = VideoAssembler(config, cost_tracker)
        shorts_gen = ShortsGenerator(config, cost_tracker, script_gen, media_gen, video_assembler)
        scheduler = Scheduler(config, state, cost_tracker)

        # Initialize workflows
        long_form_workflow = LongFormWorkflow(config, state, cost_tracker, orchestrator)
        short_form_workflow = ShortFormWorkflow(config, state, cost_tracker, orchestrator, shorts_gen)
    except Exception as e:
        print(f"Warning: Could not initialize generation modules: {e}")
        API_KEYS_CONFIGURED = False
else:
    print("ℹ️  Dashboard running in VIEW-ONLY mode")
    print("ℹ️  Add API keys in Render dashboard to enable content generation")
    script_gen = char_creator = anchor_mgr = scene_planner = None
    media_gen = video_assembler = shorts_gen = scheduler = None
    long_form_workflow = short_form_workflow = None


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('index.html')

@app.route('/channels')
def channels_page():
    """Channels management page."""
    return render_template('channels.html')

@app.route('/generate')
def generate_page():
    """Content generation page."""
    return render_template('generate.html')

@app.route('/costs')
def costs_page():
    """Cost tracking page."""
    return render_template('costs.html')

@app.route('/schedule')
def schedule_page():
    """Schedule management page."""
    return render_template('schedule.html')

@app.route('/history')
def history_page():
    """Generation history page."""
    return render_template('history.html')


# ============================================================================
# API ROUTES - SYSTEM
# ============================================================================

@app.route('/api/system/status')
def api_system_status():
    """Get system status."""
    try:
        active_channels = config.get_active_channels()
        total_channels = len(config.channels)

        # Cost summary
        global_daily = cost_tracker.get_global_costs_today()
        global_monthly = cost_tracker.get_global_costs_month()

        # Generation stats
        stats = state.get_stats()

        # Orchestrator stats
        orch_stats = orchestrator.get_stats()

        return jsonify({
            'status': 'ok',
            'api_keys_configured': API_KEYS_CONFIGURED,
            'channels': {
                'total': total_channels,
                'active': len(active_channels),
                'paused': total_channels - len(active_channels)
            },
            'costs': {
                'today': round(global_daily, 2),
                'month': round(global_monthly, 2),
                'daily_cap': config.get_system_setting('cost_management.global_daily_cost_cap', 50.0),
                'monthly_cap': config.get_system_setting('cost_management.global_monthly_cost_cap', 1000.0)
            },
            'generation': {
                'queued': stats.get('queued', 0),
                'in_progress': stats.get('script_generation', 0) + stats.get('media_generation', 0),
                'completed_today': stats.get('uploaded', 0),
                'failed': stats.get('failed', 0)
            },
            'orchestrator': orch_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/alerts')
def api_system_alerts():
    """Get system alerts."""
    try:
        alerts = cost_tracker.get_alerts()

        formatted_alerts = []
        for alert in alerts:
            formatted_alerts.append({
                'type': 'warning',
                'channel': alert['channel_name'],
                'message': f"{alert['channel_name']}: {alert['percentage']:.1f}% of daily budget used",
                'severity': 'high' if alert['percentage'] >= 90 else 'medium'
            })

        return jsonify({
            'alerts': formatted_alerts,
            'count': len(formatted_alerts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ROUTES - CHANNELS
# ============================================================================

@app.route('/api/channels')
def api_channels_list():
    """Get all channels."""
    try:
        channels = []
        for channel in config.channels:
            # Get costs for this channel
            daily_cost = cost_tracker.get_channel_costs_today(channel.channel_id)

            # Get recent videos
            recent_videos = state.get_videos_by_channel(channel.channel_id, limit=5)

            channels.append({
                'id': channel.channel_id,
                'name': channel.channel_name,
                'youtube_id': channel.youtube_channel_id,
                'niche': channel.niche,
                'status': channel.status,
                'long_form_enabled': channel.long_form_enabled,
                'shorts_enabled': channel.shorts_enabled,
                'shorts_per_day': channel.shorts_per_day,
                'use_character': channel.use_channel_character,
                'visual_style': channel.visual_style,
                'pacing_style': channel.pacing_style,
                'daily_budget': channel.api_cost_cap_per_day,
                'daily_spent': round(daily_cost, 2),
                'budget_used_pct': round((daily_cost / channel.api_cost_cap_per_day) * 100, 1),
                'recent_videos_count': len(recent_videos)
            })

        return jsonify({'channels': channels})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/channels/<channel_id>')
def api_channel_detail(channel_id):
    """Get channel details."""
    try:
        channel = config.get_channel(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        # Get detailed stats
        daily_cost = cost_tracker.get_channel_costs_today(channel_id)
        monthly_cost = cost_tracker.get_channel_costs_month(channel_id)
        breakdown = cost_tracker.get_cost_breakdown(channel_id, days=7)
        videos = state.get_videos_by_channel(channel_id, limit=20)

        return jsonify({
            'channel': {
                'id': channel.channel_id,
                'name': channel.channel_name,
                'youtube_id': channel.youtube_channel_id,
                'niche': channel.niche,
                'topic': channel.topic,
                'status': channel.status,
                'base_prompt': channel.base_prompt,
                'tone_modifiers': channel.tone_style_modifiers,
                'visual_style': channel.visual_style,
                'pacing_style': channel.pacing_style,
                'long_form_enabled': channel.long_form_enabled,
                'shorts_enabled': channel.shorts_enabled,
                'shorts_per_day': channel.shorts_per_day,
                'target_duration': channel.target_long_duration,
                'use_character': channel.use_channel_character,
                'character': channel.channel_character.__dict__ if channel.channel_character else None,
                'timezone': channel.upload_timezone,
                'schedule_long': [s.__dict__ for s in channel.upload_schedule_long],
                'schedule_shorts': [s.__dict__ for s in channel.upload_schedule_shorts],
                'daily_budget': channel.api_cost_cap_per_day
            },
            'stats': {
                'daily_cost': round(daily_cost, 2),
                'monthly_cost': round(monthly_cost, 2),
                'cost_breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                'total_videos': len(videos),
                'videos_this_week': len([v for v in videos if v['created_at'] > (datetime.now() - timedelta(days=7)).isoformat()])
            },
            'recent_videos': videos[:10]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ROUTES - GENERATION
# ============================================================================

@app.route('/api/generate/long', methods=['POST'])
def api_generate_long():
    """Trigger long-form generation."""
    try:
        # Check if API keys are configured
        if not API_KEYS_CONFIGURED:
            return jsonify({
                'error': 'API keys not configured. Add them in Render dashboard → Environment to enable generation.'
            }), 400

        data = request.json
        channel_id = data.get('channel_id')

        if not channel_id:
            return jsonify({'error': 'channel_id required'}), 400

        # Check if channel exists
        channel = config.get_channel(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        # Trigger generation asynchronously
        async def generate():
            return await long_form_workflow.execute(channel_id=channel_id, scheduled_time=datetime.now())

        video_id = asyncio.run(generate())

        return jsonify({
            'success': True,
            'video_id': video_id,
            'message': f'Long-form generation started for {channel.channel_name}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/shorts', methods=['POST'])
def api_generate_shorts():
    """Trigger shorts generation."""
    try:
        # Check if API keys are configured
        if not API_KEYS_CONFIGURED:
            return jsonify({
                'error': 'API keys not configured. Add them in Render dashboard → Environment to enable generation.'
            }), 400

        data = request.json
        channel_id = data.get('channel_id')
        num_shorts = data.get('num_shorts')

        if not channel_id:
            return jsonify({'error': 'channel_id required'}), 400

        channel = config.get_channel(channel_id)
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404

        async def generate():
            return await short_form_workflow.execute(
                channel_id=channel_id,
                num_shorts=num_shorts,
                scheduled_time=datetime.now()
            )

        video_ids = asyncio.run(generate())

        return jsonify({
            'success': True,
            'video_ids': video_ids,
            'count': len(video_ids),
            'message': f'Generated {len(video_ids)} shorts for {channel.channel_name}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/videos/<video_id>')
def api_video_detail(video_id):
    """Get video details."""
    try:
        video = state.get_video(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404

        # Get pipeline stages
        stages = state.get_pipeline_stages(video_id)

        # Get assets
        assets = state.get_assets(video_id)

        # Get cost
        cost = cost_tracker.get_video_cost(video_id)

        return jsonify({
            'video': video,
            'stages': stages,
            'assets': assets,
            'cost': round(cost, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ROUTES - COSTS
# ============================================================================

@app.route('/api/costs/summary')
def api_costs_summary():
    """Get cost summary."""
    try:
        # Global costs
        global_today = cost_tracker.get_global_costs_today()
        global_month = cost_tracker.get_global_costs_month()
        global_breakdown = cost_tracker.get_cost_breakdown(days=30)

        # Per-channel costs
        channel_costs = []
        for channel in config.get_active_channels():
            daily = cost_tracker.get_channel_costs_today(channel.channel_id)
            monthly = cost_tracker.get_channel_costs_month(channel.channel_id)

            channel_costs.append({
                'channel_id': channel.channel_id,
                'channel_name': channel.channel_name,
                'daily': round(daily, 2),
                'monthly': round(monthly, 2),
                'budget': channel.api_cost_cap_per_day,
                'usage_pct': round((daily / channel.api_cost_cap_per_day) * 100, 1)
            })

        return jsonify({
            'global': {
                'today': round(global_today, 2),
                'month': round(global_month, 2),
                'breakdown': {k: round(v, 2) for k, v in global_breakdown.items()},
                'daily_cap': config.get_system_setting('cost_management.global_daily_cost_cap', 50.0),
                'monthly_cap': config.get_system_setting('cost_management.global_monthly_cost_cap', 1000.0)
            },
            'channels': channel_costs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ROUTES - HISTORY
# ============================================================================

@app.route('/api/history')
def api_history():
    """Get generation history."""
    try:
        channel_id = request.args.get('channel_id')
        limit = int(request.args.get('limit', 50))

        if channel_id:
            videos = state.get_videos_by_channel(channel_id, limit=limit)
        else:
            # Get all videos across channels
            videos = []
            for channel in config.channels:
                channel_videos = state.get_videos_by_channel(channel.channel_id, limit=10)
                videos.extend(channel_videos)

            # Sort by created_at
            videos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            videos = videos[:limit]

        return jsonify({
            'videos': videos,
            'count': len(videos)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    # Get port from environment (for cloud deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    print("\n" + "="*60)
    print("🚀 AI Content Automation Dashboard")
    print("="*60)
    print(f"\n📊 Dashboard URL: http://localhost:{port}")
    print(f"Environment: {app.config['ENV']}")
    print(f"Debug Mode: {debug}")
    print("\nActive Channels:", len(config.get_active_channels()))
    print("Total Channels:", len(config.channels))
    print("\n" + "="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False  # Disable reloader to prevent duplicate initialization
    )
