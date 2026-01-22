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

app = Flask(__name__)
CORS(app)

# Initialize orchestrator
orchestrator = ProductionOrchestrator()
post_manager = PostManager()

# Set default kie.ai API key if not already set
if not os.environ.get('KIEAI_API_KEY'):
    os.environ['KIEAI_API_KEY'] = '74ba78915402a077bb93b3cf140eb904'

# Enable mock mode for development (set to 'false' for real generation)
os.environ['STUDIO_MOCK_GENERATION'] = 'true'
os.environ['STUDIO_MOCK_POSTING'] = 'true'


# ============================================================================
# WEB PAGES
# ============================================================================

@app.route('/')
def index():
    """Studio home page"""
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
