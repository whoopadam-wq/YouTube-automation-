#!/usr/bin/env python3
"""
Cinematic Compiler CLI
Command-line interface for standalone compiler usage
"""
import argparse
import sys
import json
from pathlib import Path

from .engine import CinematicCompiler
from .video_generator import CinematicVideoGenerator
from .state_manager import CompilerStateManager


def cmd_create(args):
    """Create a new cinematic project"""
    compiler = CinematicCompiler()

    project = compiler.create_project(
        title=args.title,
        target_platform=args.platform,
        visual_style_rules=args.style or ""
    )

    print(f"\n✨ Project created successfully!")
    print(f"   Project ID: {project.project_id}")
    print(f"\nNext steps:")
    print(f"   1. Add scenes: cinematic-cli add-scene {project.project_id}")
    print(f"   2. Compile: cinematic-cli compile {project.project_id}")


def cmd_list(args):
    """List all projects"""
    compiler = CinematicCompiler()
    projects = compiler.list_projects()

    if not projects:
        print("No projects found.")
        return

    print(f"\n{'='*80}")
    print(f"CINEMATIC PROJECTS ({len(projects)} total)")
    print(f"{'='*80}\n")

    for proj in projects:
        status = "✅ COMPLETE" if proj['complete'] else f"⏳ {proj['stage']}"
        print(f"  ID: {proj['project_id']}")
        print(f"  Title: {proj['title']}")
        print(f"  Scenes: {proj['scenes_count']}")
        print(f"  Status: {status}")
        print(f"  Created: {proj['created_at']}")
        print(f"  {'-'*76}")


def cmd_add_scene(args):
    """Add scene to project"""
    compiler = CinematicCompiler()

    project = compiler.load_project(args.project_id)
    if not project:
        print(f"❌ Project not found: {args.project_id}")
        sys.exit(1)

    scene = compiler.add_scene(
        project,
        scene_description=args.description or "",
        duration_seconds=args.duration
    )

    print(f"\n✅ Scene {scene.sequence_number} added to '{project.title}'")


def cmd_compile(args):
    """Compile a project"""
    compiler = CinematicCompiler()

    project = compiler.load_project(args.project_id)
    if not project:
        print(f"❌ Project not found: {args.project_id}")
        sys.exit(1)

    if len(project.scenes) == 0:
        print(f"❌ No scenes in project. Add scenes first.")
        sys.exit(1)

    # Compile
    project = compiler.compile_project(project)

    print(f"\n✅ Project compilation complete!")
    print(f"   {len(project.scenes)} scenes compiled")
    print(f"   {len(project.global_characters)} characters locked")


def cmd_export(args):
    """Export compiled prompts"""
    compiler = CinematicCompiler()

    project = compiler.load_project(args.project_id)
    if not project:
        print(f"❌ Project not found: {args.project_id}")
        sys.exit(1)

    if not project.compilation_complete:
        print(f"⚠️  Project not fully compiled. Exporting available prompts...")

    # Export to files
    export_path = compiler.export_prompts_to_files(project)

    print(f"\n✅ Prompts exported to: {export_path}")

    # Also export JSON if requested
    if args.format == "json":
        json_path = Path(export_path) / "prompts.json"
        prompts = compiler.get_compiled_prompts(project)

        with open(json_path, 'w') as f:
            json.dump(prompts, f, indent=2)

        print(f"   JSON: {json_path}")


def cmd_generate(args):
    """Generate videos from compiled project"""
    compiler = CinematicCompiler()

    project = compiler.load_project(args.project_id)
    if not project:
        print(f"❌ Project not found: {args.project_id}")
        sys.exit(1)

    if not project.compilation_complete:
        print(f"❌ Project must be compiled before generation")
        sys.exit(1)

    # Generate videos
    generator = CinematicVideoGenerator()
    results = generator.generate_project_full(project)

    print(f"\n✅ Generation complete!")
    print(f"   {len(results)} videos generated")


def cmd_info(args):
    """Show project info"""
    compiler = CinematicCompiler()

    project = compiler.load_project(args.project_id)
    if not project:
        print(f"❌ Project not found: {args.project_id}")
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"PROJECT: {project.title}")
    print(f"{'='*80}")
    print(f"  ID: {project.project_id}")
    print(f"  Created: {project.created_at}")
    print(f"  Platform: {project.target_platform}")
    print(f"  Resolution: {project.target_resolution}")
    print(f"  FPS: {project.target_fps}")
    print(f"  Status: {'✅ Complete' if project.compilation_complete else f'⏳ {project.current_stage.value}'}")
    print(f"\n  SCENES: {len(project.scenes)}")
    for scene in project.scenes:
        status = "🔒 Locked" if scene.locked else "📝 Draft"
        print(f"    {scene.sequence_number}. Scene {scene.scene_id} - {status} ({scene.duration_seconds}s)")

    print(f"\n  CHARACTERS: {len(project.global_characters)}")
    for char_id, char in project.global_characters.items():
        print(f"    - {char.canonical_name} ({char_id})")

    print(f"\n  VISUAL STYLE:")
    print(f"    {project.visual_style_rules or 'Not set'}")
    print(f"{'='*80}\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Cinematic Production Compiler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create project
  cinematic-cli create "My Film" --platform veo3

  # Add scenes
  cinematic-cli add-scene cin_abc123 --description "Opening scene"

  # Compile
  cinematic-cli compile cin_abc123

  # Export prompts
  cinematic-cli export cin_abc123 --format json

  # Generate videos
  cinematic-cli generate cin_abc123
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create project
    create_parser = subparsers.add_parser('create', help='Create new project')
    create_parser.add_argument('title', help='Project title')
    create_parser.add_argument('--platform', default='veo3', choices=['veo3', 'nanoBanana', 'both'])
    create_parser.add_argument('--style', help='Visual style rules')
    create_parser.set_defaults(func=cmd_create)

    # List projects
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.set_defaults(func=cmd_list)

    # Add scene
    add_scene_parser = subparsers.add_parser('add-scene', help='Add scene to project')
    add_scene_parser.add_argument('project_id', help='Project ID')
    add_scene_parser.add_argument('--description', help='Scene description')
    add_scene_parser.add_argument('--duration', type=float, default=5.0, help='Duration in seconds')
    add_scene_parser.set_defaults(func=cmd_add_scene)

    # Compile
    compile_parser = subparsers.add_parser('compile', help='Compile project')
    compile_parser.add_argument('project_id', help='Project ID')
    compile_parser.set_defaults(func=cmd_compile)

    # Export
    export_parser = subparsers.add_parser('export', help='Export compiled prompts')
    export_parser.add_argument('project_id', help='Project ID')
    export_parser.add_argument('--format', choices=['txt', 'json'], default='txt')
    export_parser.set_defaults(func=cmd_export)

    # Generate
    generate_parser = subparsers.add_parser('generate', help='Generate videos')
    generate_parser.add_argument('project_id', help='Project ID')
    generate_parser.set_defaults(func=cmd_generate)

    # Info
    info_parser = subparsers.add_parser('info', help='Show project info')
    info_parser.add_argument('project_id', help='Project ID')
    info_parser.set_defaults(func=cmd_info)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
