"""
Flask API Routes for Cinematic Compiler
Adds REST API endpoints to the studio Flask app
"""
from flask import Blueprint, request, jsonify
from studio.cinematic_compiler import CinematicCompiler, CinematicScene
from studio.cinematic_compiler.video_generator import CinematicVideoGenerator


# Create blueprint
cinematic_bp = Blueprint('cinematic', __name__, url_prefix='/api/cinematic')

# Initialize compiler (singleton)
compiler = CinematicCompiler()
generator = CinematicVideoGenerator()


@cinematic_bp.route('/projects', methods=['GET'])
def list_projects():
    """List all cinematic projects"""
    projects = compiler.list_projects()
    return jsonify(projects)


@cinematic_bp.route('/projects', methods=['POST'])
def create_project():
    """
    Create new cinematic project

    Body:
    {
        "title": "Project Title",
        "target_platform": "veo3",
        "visual_style_rules": "Optional style rules"
    }
    """
    data = request.get_json()

    title = data.get('title')
    if not title:
        return jsonify({"error": "Title required"}), 400

    platform = data.get('target_platform', 'veo3')
    style = data.get('visual_style_rules', '')

    project = compiler.create_project(title, platform, style)

    return jsonify({
        "project_id": project.project_id,
        "title": project.title,
        "target_platform": project.target_platform,
        "created_at": project.created_at.isoformat()
    }), 201


@cinematic_bp.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get project details"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    return jsonify(project.to_dict())


@cinematic_bp.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project"""
    success = compiler.state_manager.delete_project(project_id)

    if not success:
        return jsonify({"error": "Project not found"}), 404

    return jsonify({"message": "Project deleted"}), 200


@cinematic_bp.route('/projects/<project_id>/scenes', methods=['POST'])
def add_scene(project_id):
    """
    Add scene to project

    Body:
    {
        "description": "Optional scene description",
        "duration_seconds": 5.0
    }
    """
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json() or {}

    scene = compiler.add_scene(
        project,
        scene_description=data.get('description', ''),
        duration_seconds=data.get('duration_seconds', 5.0)
    )

    return jsonify({
        "scene_id": scene.scene_id,
        "sequence_number": scene.sequence_number,
        "duration_seconds": scene.duration_seconds
    }), 201


@cinematic_bp.route('/projects/<project_id>/compile', methods=['POST'])
def compile_project(project_id):
    """
    Compile all scenes in project

    Body (optional):
    {
        "auto_save": true
    }
    """
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    if len(project.scenes) == 0:
        return jsonify({"error": "No scenes to compile"}), 400

    data = request.get_json() or {}
    auto_save = data.get('auto_save', True)

    # Compile project
    project = compiler.compile_project(project)

    return jsonify({
        "project_id": project.project_id,
        "compilation_complete": project.compilation_complete,
        "scenes_compiled": len(project.scenes),
        "characters_locked": len(project.global_characters)
    }), 200


@cinematic_bp.route('/projects/<project_id>/prompts', methods=['GET'])
def get_prompts(project_id):
    """Get all compiled prompts"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    prompts = compiler.get_compiled_prompts(project)

    return jsonify({
        "project_id": project.project_id,
        "prompts": prompts
    })


@cinematic_bp.route('/projects/<project_id>/export/veo', methods=['GET'])
def export_veo(project_id):
    """Export in Veo 3 API format"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    veo_requests = compiler.export_for_veo(project)

    return jsonify({
        "project_id": project.project_id,
        "platform": "veo3",
        "requests": veo_requests
    })


@cinematic_bp.route('/projects/<project_id>/export/nanoBanana', methods=['GET'])
def export_nano_banana(project_id):
    """Export in Nano Banana API format"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    nb_requests = compiler.export_for_nano_banana(project)

    return jsonify({
        "project_id": project.project_id,
        "platform": "nanoBanana",
        "requests": nb_requests
    })


@cinematic_bp.route('/projects/<project_id>/generate', methods=['POST'])
def generate_videos(project_id):
    """
    Generate videos for all scenes

    Body (optional):
    {
        "scene_ids": ["scene_1", "scene_2"]  # Optional: generate specific scenes only
    }
    """
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    if not project.compilation_complete:
        return jsonify({"error": "Project must be compiled first"}), 400

    data = request.get_json() or {}
    scene_ids = data.get('scene_ids')

    # Generate videos
    try:
        results = generator.generate_project_full(project)

        return jsonify({
            "project_id": project.project_id,
            "scenes_generated": len(results),
            "results": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cinematic_bp.route('/projects/<project_id>/scenes/<scene_id>/generate', methods=['POST'])
def generate_scene(project_id, scene_id):
    """Generate video for a single scene"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    # Find scene
    scene = next((s for s in project.scenes if s.scene_id == scene_id), None)

    if not scene:
        return jsonify({"error": "Scene not found"}), 404

    if not scene.locked:
        return jsonify({"error": "Scene must be compiled first"}), 400

    # Generate
    try:
        result = generator.generate_scene_full(scene, project)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cinematic_bp.route('/projects/<project_id>/characters', methods=['GET'])
def get_characters(project_id):
    """Get all locked characters"""
    project = compiler.load_project(project_id)

    if not project:
        return jsonify({"error": "Project not found"}), 404

    characters = [char.to_dict() for char in project.global_characters.values()]

    return jsonify({
        "project_id": project.project_id,
        "characters": characters
    })


@cinematic_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "cinematic-compiler",
        "version": "1.0.0"
    })


# Error handlers
@cinematic_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@cinematic_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
