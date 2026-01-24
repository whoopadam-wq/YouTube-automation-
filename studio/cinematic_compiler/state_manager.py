"""
Cinematic Compiler State Manager
Handles persistent storage and retrieval of project state
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .schemas import CinematicProject, CinematicScene, CharacterIdentity


class CompilerStateManager:
    """
    Manages persistent state for cinematic compiler projects

    State is stored as JSON files in data/cinematic_projects/
    Each project has its own file: {project_id}.json

    This enables:
    - Session persistence across conversations
    - Character/location immutability
    - Resume capability
    - State inspection
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize state manager

        Args:
            data_dir: Directory for storing project files (default: data/cinematic_projects/)
        """
        if data_dir is None:
            # Use project root data directory
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data" / "cinematic_projects"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 CompilerStateManager initialized: {self.data_dir}")

    def save_project(self, project: CinematicProject) -> str:
        """
        Save project to persistent storage

        Args:
            project: CinematicProject to save

        Returns:
            File path where project was saved
        """
        file_path = self.data_dir / f"{project.project_id}.json"

        # Serialize to dict
        project_data = project.to_dict()

        # Add metadata
        project_data['_saved_at'] = datetime.now().isoformat()
        project_data['_version'] = '1.0.0'

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Project saved: {file_path}")
        return str(file_path)

    def load_project(self, project_id: str) -> Optional[CinematicProject]:
        """
        Load project from persistent storage

        Args:
            project_id: ID of project to load

        Returns:
            CinematicProject if found, None otherwise
        """
        file_path = self.data_dir / f"{project_id}.json"

        if not file_path.exists():
            print(f"⚠️  Project not found: {project_id}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # Deserialize
        project = CinematicProject.from_dict(project_data)

        # Reconstruct complex objects
        project = self._reconstruct_project(project_data, project)

        print(f"📂 Project loaded: {project_id} ({len(project.scenes)} scenes)")
        return project

    def list_projects(self) -> List[Dict[str, any]]:
        """
        List all saved projects

        Returns:
            List of project metadata dicts
        """
        projects = []

        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                projects.append({
                    "project_id": data.get("project_id"),
                    "title": data.get("title"),
                    "created_at": data.get("created_at"),
                    "saved_at": data.get("_saved_at"),
                    "scenes_count": len(data.get("scenes", [])),
                    "stage": data.get("current_stage"),
                    "complete": data.get("compilation_complete", False)
                })
            except Exception as e:
                print(f"⚠️  Failed to load project metadata from {file_path}: {e}")

        # Sort by created_at descending
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return projects

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project from storage

        Args:
            project_id: ID of project to delete

        Returns:
            True if deleted, False if not found
        """
        file_path = self.data_dir / f"{project_id}.json"

        if not file_path.exists():
            print(f"⚠️  Project not found: {project_id}")
            return False

        file_path.unlink()
        print(f"🗑️  Project deleted: {project_id}")
        return True

    def get_character_from_memory(self, project_id: str, character_id: str) -> Optional[CharacterIdentity]:
        """
        Retrieve a locked character identity from project memory

        Args:
            project_id: Project ID
            character_id: Character ID

        Returns:
            CharacterIdentity if found, None otherwise
        """
        project = self.load_project(project_id)

        if not project:
            return None

        return project.global_characters.get(character_id)

    def lock_character(self, project_id: str, character: CharacterIdentity) -> bool:
        """
        Lock a character identity in project memory (immutable once locked)

        Args:
            project_id: Project ID
            character: CharacterIdentity to lock

        Returns:
            True if locked, False if failed
        """
        project = self.load_project(project_id)

        if not project:
            print(f"⚠️  Cannot lock character: project {project_id} not found")
            return False

        # Check if already locked
        if character.character_id in project.global_characters:
            existing = project.global_characters[character.character_id]
            if existing.identity_locked:
                print(f"⚠️  Character already locked: {character.character_id}")
                print(f"   Cannot modify immutable identity")
                return False

        # Lock the character
        character.identity_locked = True
        project.global_characters[character.character_id] = character

        # Save
        self.save_project(project)
        print(f"🔒 Character locked: {character.canonical_name} ({character.character_id})")

        return True

    def _reconstruct_project(self, data: Dict, project: CinematicProject) -> CinematicProject:
        """
        Reconstruct complex nested objects from dict data

        Args:
            data: Raw dict data
            project: Partially initialized project

        Returns:
            Fully reconstructed project
        """
        # Reconstruct global characters
        if 'global_characters' in data:
            for char_id, char_data in data['global_characters'].items():
                project.global_characters[char_id] = self._dict_to_character(char_data)

        # Reconstruct scenes (this will be expanded to handle all nested objects)
        if 'scenes' in data:
            from .schemas import (
                CinematicScene, NarrativeBeat, PhysicalReality,
                SpatialState, CameraSpec, LightingPhysics,
                CompositionRules, MotionDelta, CompiledPrompt, FrameType
            )

            scenes = []
            for scene_data in data['scenes']:
                scene = CinematicScene(
                    scene_id=scene_data['scene_id'],
                    sequence_number=scene_data['sequence_number'],
                    duration_seconds=scene_data.get('duration_seconds', 5.0),
                    locked=scene_data.get('locked', False)
                )

                # Reconstruct narrative
                if scene_data.get('narrative'):
                    scene.narrative = NarrativeBeat(**scene_data['narrative'])

                # Reconstruct physical reality
                if scene_data.get('physical_reality'):
                    scene.physical_reality = PhysicalReality(**scene_data['physical_reality'])

                # Reconstruct character identities
                if scene_data.get('character_identities'):
                    scene.character_identities = [
                        self._dict_to_character(c) for c in scene_data['character_identities']
                    ]

                # Reconstruct spatial state
                if scene_data.get('spatial_state'):
                    scene.spatial_state = SpatialState(**scene_data['spatial_state'])

                # Reconstruct camera
                if scene_data.get('camera'):
                    scene.camera = CameraSpec(**scene_data['camera'])

                # Reconstruct lighting
                if scene_data.get('lighting'):
                    scene.lighting = LightingPhysics(**scene_data['lighting'])

                # Reconstruct composition
                if scene_data.get('composition'):
                    scene.composition = CompositionRules(**scene_data['composition'])

                # Reconstruct motion
                if scene_data.get('motion'):
                    scene.motion = MotionDelta(**scene_data['motion'])

                # Reconstruct compiled prompts
                if scene_data.get('start_frame_prompt'):
                    prompt_data = scene_data['start_frame_prompt']
                    scene.start_frame_prompt = CompiledPrompt(
                        frame_type=FrameType(prompt_data['frame_type']),
                        characters=prompt_data.get('characters', ''),
                        environment=prompt_data.get('environment', ''),
                        camera=prompt_data.get('camera', ''),
                        lighting=prompt_data.get('lighting', ''),
                        composition=prompt_data.get('composition', ''),
                        motion=prompt_data.get('motion', ''),
                        anti_ai_rules=prompt_data.get('anti_ai_rules', ''),
                        full_prompt=prompt_data.get('full_prompt', '')
                    )

                if scene_data.get('end_frame_prompt'):
                    prompt_data = scene_data['end_frame_prompt']
                    scene.end_frame_prompt = CompiledPrompt(
                        frame_type=FrameType(prompt_data['frame_type']),
                        characters=prompt_data.get('characters', ''),
                        environment=prompt_data.get('environment', ''),
                        camera=prompt_data.get('camera', ''),
                        lighting=prompt_data.get('lighting', ''),
                        composition=prompt_data.get('composition', ''),
                        motion=prompt_data.get('motion', ''),
                        anti_ai_rules=prompt_data.get('anti_ai_rules', ''),
                        full_prompt=prompt_data.get('full_prompt', '')
                    )

                scenes.append(scene)

            project.scenes = scenes

        # Reconstruct global locations
        if 'global_locations' in data:
            project.global_locations = data['global_locations']

        if 'visual_style_rules' in data:
            project.visual_style_rules = data['visual_style_rules']

        return project

    def _dict_to_character(self, data: Dict) -> CharacterIdentity:
        """Convert dict to CharacterIdentity"""
        return CharacterIdentity(
            character_id=data['character_id'],
            canonical_name=data['canonical_name'],
            age=data['age'],
            ethnicity=data['ethnicity'],
            bone_structure=data['bone_structure'],
            face_shape=data['face_shape'],
            distinctive_features=data['distinctive_features'],
            hair_description=data['hair_description'],
            facial_hair=data.get('facial_hair', ''),
            body_type=data['body_type'],
            height_relative=data['height_relative'],
            posture_tendencies=data['posture_tendencies'],
            wardrobe=data['wardrobe'],
            accessories=data.get('accessories', ''),
            reference_image_url=data.get('reference_image_url'),
            identity_locked=data.get('identity_locked', True)
        )

    def export_prompts(self, project_id: str, output_dir: Optional[str] = None) -> str:
        """
        Export all compiled prompts to text files for external use

        Args:
            project_id: Project ID
            output_dir: Directory to export to (default: data/exports/)

        Returns:
            Path to export directory
        """
        project = self.load_project(project_id)

        if not project:
            raise ValueError(f"Project not found: {project_id}")

        if output_dir is None:
            output_dir = self.data_dir.parent / "exports" / project_id

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export each scene's prompts
        for scene in project.scenes:
            if scene.start_frame_prompt and scene.end_frame_prompt:
                scene_file = output_path / f"scene_{scene.sequence_number:03d}.txt"

                with open(scene_file, 'w', encoding='utf-8') as f:
                    f.write(f"SCENE {scene.sequence_number}\n")
                    f.write("=" * 80 + "\n\n")

                    f.write("START FRAME PROMPT:\n")
                    f.write("-" * 80 + "\n")
                    f.write(scene.start_frame_prompt.full_prompt + "\n\n")

                    f.write("END FRAME PROMPT:\n")
                    f.write("-" * 80 + "\n")
                    f.write(scene.end_frame_prompt.full_prompt + "\n\n")

                    f.write(f"DURATION: {scene.duration_seconds}s\n")
                    if scene.motion:
                        f.write(f"MOTION: {scene.motion.motion_description}\n")

        print(f"📤 Exported {len(project.scenes)} scenes to: {output_path}")
        return str(output_path)
