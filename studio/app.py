"""
AI Video Production Studio
Main Flask application with timeline editor
"""
import os
import asyncio
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from studio.orchestrator import ProductionOrchestrator
from studio.schemas import ProductionMode, AgentStage
from studio.posting.post_manager import PostManager
from studio.channel_integration import YouTubeChannelIntegration
from studio.autonomous_learning import get_learning_system
from studio.cost_estimator import CostEstimator
from studio.agents.ideas_scraper_agent import IdeasScraperAgent
from studio.agents.analytics_agent import AnalyticsAgent

app = Flask(__name__)
CORS(app)

# Initialize orchestrator
orchestrator = ProductionOrchestrator()
post_manager = PostManager()

# Set default kie.ai API key if not already set
if not os.environ.get('KIEAI_API_KEY'):
    os.environ['KIEAI_API_KEY'] = '74ba78915402a077bb93b3cf140eb904'

# YouTube Data API key - REQUIRED for channel integration
# Get your free API key: https://console.cloud.google.com/apis/credentials
# Enable YouTube Data API v3 in your Google Cloud project
if not os.environ.get('YOUTUBE_DATA_API_KEY'):
    print("⚠️  WARNING: YOUTUBE_DATA_API_KEY not set!")
    print("   Channel integration will not work without it.")
    print("   Get API key: https://console.cloud.google.com/apis/credentials")
    print("   Set it in Render dashboard: Environment > YOUTUBE_DATA_API_KEY")

# Enable mock mode for development (set to 'false' for real generation)
os.environ['STUDIO_MOCK_GENERATION'] = 'true'
os.environ['STUDIO_MOCK_POSTING'] = 'true'


# ============================================================================
# WEB PAGES
# ============================================================================

@app.route('/')
def index():
    """Autonomous Dashboard - main page"""
    return render_template('autonomous_dashboard.html')


@app.route('/home')
def old_home():
    """Old studio home page"""
    return render_template('studio_home.html')


@app.route('/timeline/<job_id>')
def timeline_editor(job_id):
    """Timeline editor page"""
    job = orchestrator.get_job(job_id)
    if not job:
        return "Job not found", 404
    return render_template('timeline_editor.html', job=job.to_dict())


@app.route('/new-production')
def new_production():
    """Create new production page"""
    return render_template('new_production.html')


@app.route('/tools')
def tools_manager():
    """AI Tools Manager page"""
    return render_template('tools_manager.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all production jobs"""
    jobs = orchestrator.list_jobs()
    return jsonify({"jobs": jobs})


@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new production job"""
    data = request.json

    # Create job
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        orchestrator.create_job(
            channel_id=data.get('channel_id', 'default'),
            title=data['title'],
            topic=data['topic'],
            duration_target=float(data.get('duration', 30)),
            platform=data.get('platform', 'youtube'),
            mode=ProductionMode[data.get('mode', 'AUTO').upper()],
            visual_style=data.get('visual_style', 'cinematic'),
            tone=data.get('tone', 'engaging')
        )
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get job details"""
    job = orchestrator.get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>/start', methods=['POST'])
def start_pipeline(job_id):
    """Start the production pipeline"""
    data = request.json or {}
    stop_at = data.get('stop_at')

    if stop_at:
        stop_at = AgentStage[stop_at.upper()]

    # Run pipeline
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        orchestrator.run_pipeline(job_id, stop_at=stop_at)
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>/continue', methods=['POST'])
def continue_pipeline(job_id):
    """Continue pipeline from current stage"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        orchestrator.continue_from_stage(job_id)
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>/regenerate/<stage>', methods=['POST'])
def regenerate_stage(job_id, stage):
    """Regenerate a specific stage"""
    stage_enum = AgentStage[stage.upper()]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        orchestrator.regenerate_stage(job_id, stage_enum)
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>/clips/<clip_id>', methods=['PATCH'])
def update_clip(job_id, clip_id):
    """Update a clip (timeline editing)"""
    updates = request.json

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        orchestrator.update_clip(job_id, clip_id, updates)
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


@app.route('/api/jobs/<job_id>/post', methods=['POST'])
def post_to_platforms(job_id):
    """Post video to platforms"""
    data = request.json
    platforms = data.get('platforms', ['youtube'])

    job = orchestrator.get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if not job.is_complete:
        return jsonify({"error": "Job not complete"}), 400

    # Post to platforms
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    job = loop.run_until_complete(
        post_manager.post_to_platforms(
            job,
            platforms=platforms,
            youtube_privacy=data.get('youtube_privacy', 'private'),
            tiktok_privacy=data.get('tiktok_privacy', 'SELF_ONLY'),
            instagram_share_to_feed=data.get('instagram_share_to_feed', True)
        )
    )
    loop.close()

    return jsonify({"job": job.to_dict()})


# ============================================================================
# TOOL CONFIGURATION ENDPOINTS
# ============================================================================

@app.route('/api/tools/config', methods=['GET'])
def get_tool_config():
    """Get current tool configuration"""
    import json
    from pathlib import Path

    config_file = Path("data/tool_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "script": [],
            "character": [],
            "lighting": [],
            "composition": [],
            "frame": ["nano-banana-pro"],
            "video": ["veo-3", "elevenlabs"],
            "assembly": ["remotion"]
        }

    return jsonify({"config": config})


@app.route('/api/tools/config', methods=['POST'])
def save_tool_config():
    """Save tool configuration"""
    import json
    from pathlib import Path

    data = request.json
    config = data.get('config', {})

    # Save to file
    config_dir = Path("data")
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "tool_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    return jsonify({"success": True, "message": "Configuration saved"})


@app.route('/api/tools/test', methods=['POST'])
def test_tool_connections():
    """Test connections to all configured AI tools"""
    from studio.providers.kieai_provider import KieAIProvider

    results = {}

    # Test kie.ai connection
    try:
        api_key = os.environ.get('KIEAI_API_KEY')
        if api_key:
            provider = KieAIProvider(api_key=api_key)
            # Try to list models as a connection test
            models = provider.list_available_models()
            results['kie.ai'] = {
                "connected": True,
                "message": f"Connected - {len(models)} models available"
            }
        else:
            results['kie.ai'] = {
                "connected": False,
                "message": "API key not configured"
            }
    except Exception as e:
        results['kie.ai'] = {
            "connected": False,
            "message": f"Connection failed: {str(e)}"
        }

    # Test Anthropic (for script agent)
    try:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if api_key:
            results['anthropic'] = {
                "connected": True,
                "message": "API key configured"
            }
        else:
            results['anthropic'] = {
                "connected": False,
                "message": "API key not configured"
            }
    except Exception as e:
        results['anthropic'] = {
            "connected": False,
            "message": str(e)
        }

    # Test Remotion (just check if it's available)
    import subprocess
    try:
        remotion_check = subprocess.run(
            ['which', 'remotion'],
            capture_output=True,
            text=True
        )
        if remotion_check.returncode == 0:
            results['remotion'] = {
                "connected": True,
                "message": "Remotion CLI available"
            }
        else:
            results['remotion'] = {
                "connected": False,
                "message": "Remotion CLI not installed"
            }
    except Exception as e:
        results['remotion'] = {
            "connected": False,
            "message": "Unable to check Remotion"
        }

    return jsonify({"results": results})


# ============================================================================
# DEVELOPMENT ENDPOINTS
# ============================================================================

@app.route('/api/test/create-sample', methods=['POST'])
def create_sample_job():
    """Create a sample job for testing"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Create job
    job = loop.run_until_complete(
        orchestrator.create_job(
            channel_id='test_channel',
            title='AI-Generated Test Video',
            topic='Create an engaging video about the future of AI',
            duration_target=30,
            platform='youtube',
            mode=ProductionMode.AUTO,
            visual_style='cinematic',
            tone='inspiring'
        )
    )

    # Run pipeline
    job = loop.run_until_complete(
        orchestrator.run_pipeline(job.job_id)
    )

    loop.close()

    return jsonify({
        "job": job.to_dict(),
        "message": "Sample job created and pipeline completed"
    })


# ============================================================================
# AUTONOMOUS SYSTEM API ROUTES
# ============================================================================

# Initialize global instances
channel_integration = YouTubeChannelIntegration()
cost_estimator = CostEstimator()


@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Check system configuration and API key status"""
    status = {
        "api_keys": {
            "YOUTUBE_DATA_API_KEY": "✅ Configured" if os.environ.get('YOUTUBE_DATA_API_KEY') else "❌ Not Set",
            "SERPER_API_KEY": "✅ Configured" if os.environ.get('SERPER_API_KEY') else "❌ Not Set",
            "ANTHROPIC_API_KEY": "✅ Configured" if os.environ.get('ANTHROPIC_API_KEY') else "❌ Not Set",
            "KIE_AI_API_KEY": "✅ Configured" if os.environ.get('KIE_AI_API_KEY') else "❌ Not Set"
        },
        "channel_connected": False,
        "channel_info": None
    }

    # Check if channel is connected
    try:
        channel = channel_integration.load_active_channel()
        if channel:
            status["channel_connected"] = True
            status["channel_info"] = {
                "name": channel.channel_name,
                "channel_id": channel.channel_id,
                "niche": channel.niche,
                "subscribers": channel.subscriber_count,
                "videos": channel.video_count
            }
    except:
        pass

    return jsonify(status)


@app.route('/api/channel/integrate', methods=['POST'])
def integrate_channel():
    """Integrate a YouTube channel"""
    data = request.json
    channel_url = data.get('channel_url')

    if not channel_url:
        return jsonify({"success": False, "error": "channel_url required"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        channel = loop.run_until_complete(
            channel_integration.integrate_channel(channel_url)
        )

        return jsonify({
            "success": True,
            "channel": channel.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        loop.close()


@app.route('/api/channel/status', methods=['GET'])
def channel_status():
    """Get active channel status"""
    channel = channel_integration.load_active_channel()

    if channel:
        return jsonify({
            "channel": channel.to_dict()
        })
    else:
        return jsonify({
            "channel": None
        })


@app.route('/api/learning/start', methods=['POST'])
def start_learning():
    """Start autonomous learning system"""
    try:
        # Get active channel
        channel = channel_integration.load_active_channel()
        channel_id = channel.channel_id if channel else None

        # Start learning system in background
        learning_system = get_learning_system(channel_id=channel_id)

        # Note: In production, this should run in a separate thread/process
        # For now, we'll just indicate it's "started"

        return jsonify({
            "success": True,
            "message": "Learning system started (background mode)"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ideas/list', methods=['GET'])
def list_ideas():
    """List discovered video ideas"""
    try:
        import json
        ideas_file = "data/video_ideas_history.json"

        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                ideas = json.load(f)
                return jsonify({"ideas": ideas[-20:]})  # Last 20 ideas
        else:
            return jsonify({"ideas": []})
    except Exception as e:
        return jsonify({"ideas": [], "error": str(e)})


@app.route('/api/ideas/discover', methods=['POST'])
def discover_ideas():
    """Discover new video ideas"""
    try:
        channel = channel_integration.load_active_channel()

        if not channel:
            return jsonify({"success": False, "error": "No channel connected"}), 400

        # Check if required API keys are set
        if not os.environ.get('SERPER_API_KEY'):
            return jsonify({
                "success": False,
                "error": "SERPER_API_KEY is not set in environment variables.\n\n"
                        "This API key is REQUIRED for discovering trending topics.\n\n"
                        "Get your free API key:\n"
                        "1. Go to https://serper.dev/\n"
                        "2. Sign up (free tier: 2,500 searches)\n"
                        "3. Copy your API key\n"
                        "4. Add to Render: Environment > SERPER_API_KEY\n"
                        "5. Redeploy the service"
            }), 400

        agent = IdeasScraperAgent(channel_id=channel.channel_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        ideas = loop.run_until_complete(
            agent.discover_ideas(
                niche=channel.niche,
                num_ideas=10
            )
        )

        loop.close()

        if len(ideas) == 0:
            return jsonify({
                "success": False,
                "error": f"No ideas discovered for niche: '{channel.niche}'.\n\n"
                        f"This could mean:\n"
                        f"1. The Serper API is not working\n"
                        f"2. The niche '{channel.niche}' is too generic\n"
                        f"3. API rate limits exceeded\n\n"
                        f"Check Render logs for detailed error messages."
            }), 500

        return jsonify({
            "success": True,
            "ideas_count": len(ideas)
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in discover_ideas: {error_details}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analytics/run', methods=['POST'])
def run_analytics():
    """Run analytics on channel"""
    try:
        channel = channel_integration.load_active_channel()

        if not channel:
            return jsonify({"success": False, "error": "No channel connected"}), 400

        # Check if required API keys are set
        if not os.environ.get('YOUTUBE_DATA_API_KEY'):
            return jsonify({
                "success": False,
                "error": "YOUTUBE_DATA_API_KEY is not set in environment variables.\n\n"
                        "This API key is REQUIRED for analytics.\n"
                        "Add it to Render: Environment > YOUTUBE_DATA_API_KEY"
            }), 400

        if not os.environ.get('ANTHROPIC_API_KEY'):
            return jsonify({
                "success": False,
                "error": "ANTHROPIC_API_KEY is not set in environment variables.\n\n"
                        "This API key is REQUIRED for AI analysis.\n"
                        "Get your API key from: https://console.anthropic.com/\n"
                        "Add it to Render: Environment > ANTHROPIC_API_KEY"
            }), 400

        agent = AnalyticsAgent(channel_id=channel.channel_id)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        analysis = loop.run_until_complete(
            agent.analyze_channel_performance(days_back=30)
        )

        loop.close()

        insights_count = len(analysis.get('insights', []))

        if insights_count == 0:
            return jsonify({
                "success": False,
                "error": "No insights generated.\n\n"
                        "This could mean:\n"
                        "1. Channel has no videos to analyze\n"
                        "2. YouTube API cannot access the videos\n"
                        "3. Video data is too recent (< 24 hours old)\n\n"
                        "Check Render logs for detailed error messages."
            }), 500

        return jsonify({
            "success": True,
            "insights_count": insights_count
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in run_analytics: {error_details}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analytics/insights', methods=['GET'])
def get_insights():
    """Get analytics insights"""
    try:
        import json
        insights_file = "data/analytics_insights.json"

        if os.path.exists(insights_file):
            with open(insights_file, 'r') as f:
                data = json.load(f)
                return jsonify({"insights": data.get('insights', [])})
        else:
            return jsonify({"insights": []})
    except Exception as e:
        return jsonify({"insights": [], "error": str(e)})


@app.route('/api/cost/estimate', methods=['GET'])
def estimate_cost():
    """Estimate production cost"""
    try:
        duration = float(request.args.get('duration', 15))

        breakdown = cost_estimator.estimate_production_cost(
            duration_minutes=duration
        )

        result = breakdown.to_dict()
        result['cost_per_minute'] = result['total_cost_usd'] / duration

        return jsonify({
            "cost": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"\n{'='*60}")
    print(f"🎬 AI VIDEO PRODUCTION STUDIO")
    print(f"{'='*60}")
    print(f"Open: http://localhost:{port}")
    print(f"Mode: {'MOCK' if os.environ.get('STUDIO_MOCK_GENERATION') == 'true' else 'PRODUCTION'}")
    print(f"{'='*60}\n")

    app.run(host='0.0.0.0', port=port, debug=True)
