"""
Agent 3: Character Identity Agent
Creates absolute identity anchors
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, CharacterIdentity


class CharacterIdentityAgent(BaseCompilerAgent):
    """
    AGENT 3: CHARACTER IDENTITY

    Purpose: Create absolute identity anchors

    Responsibilities:
    - Define characters ONCE
    - Lock face, age, ethnicity, bone structure
    - Lock wardrobe and gear
    - Lock hair, facial hair, posture tendencies

    Rules:
    - Characters are immutable once locked
    - Future scenes MUST reuse identity blocks verbatim
    - No emotions unless physically visible
    - No cinematic adjectives
    """

    def __init__(self):
        super().__init__("Character Identity Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Lock character identities for this scene"""

        if not self.validate_input(scene, ['physical_reality']):
            raise ValueError(f"Scene {scene.scene_id} missing physical reality data")

        self.log(f"Locking character identities for scene {scene.sequence_number}")

        # Get characters present in scene
        character_ids = scene.physical_reality.characters_present

        scene.character_identities = []

        for char_id in character_ids:
            # Check if character already locked in global memory
            if char_id in project.global_characters:
                # Reuse immutable identity
                char = project.global_characters[char_id]
                self.log(f"  ✓ Reusing locked identity: {char.canonical_name}")
            else:
                # Create new identity (would use Claude in production)
                char = self._create_character_identity(char_id, project)
                # Lock in global memory
                project.global_characters[char_id] = char
                self.log(f"  🔒 New identity locked: {char.canonical_name}")

            scene.character_identities.append(char)

        self.log(f"✓ {len(scene.character_identities)} characters locked")

        return scene

    def _create_character_identity(self, char_id: str, project: CinematicProject) -> CharacterIdentity:
        """Create new character identity (placeholder - would use Claude API)"""

        return CharacterIdentity(
            character_id=char_id,
            canonical_name=f"Character_{char_id}",
            age="30-35",
            ethnicity="neutral",
            bone_structure="average",
            face_shape="oval",
            distinctive_features="none",
            hair_description="short dark hair",
            facial_hair="clean shaven",
            body_type="average",
            height_relative="average",
            posture_tendencies="upright",
            wardrobe="casual modern clothing",
            accessories="none",
            identity_locked=True
        )
