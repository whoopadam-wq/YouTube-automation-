# Cinematic Production Compiler

**A deterministic multi-agent system for generating high-fidelity cinematic video prompts**

Version: 1.0.0

---

## Overview

The Cinematic Production Compiler is a **structure-first, creativity-constrained** system that operates as a **COMPILER, not a writer**.

Unlike traditional AI prompt generation which produces vague, inconsistent outputs, this system enforces:

- **Deterministic compilation**: Each transformation adds information without overwriting prior decisions
- **Immutable state**: Characters, locations, and visual rules are locked once defined
- **Anti-AI enforcement**: Removes plastic skin, symmetry correction, and other AI artifacts
- **Documentary realism**: Enforces photographic camera specs and natural lighting
- **Persistent memory**: State survives across sessions and conversations

---

## Architecture

### 9-Agent Sequential Pipeline

The compiler operates as a transformation chain where each agent adds specific information:

```
Text → Structure → Identity → Space → Camera → Light → Motion → Continuity → Output Prompt
```

#### Agent 1: Idea & Narrative Agent
**Purpose**: Extract story meaning without visuals

- Identifies narrative beats
- Emotional intent
- Cause→effect relationships
- Continuity requirements

**Rules**: No camera, no lighting, no visual adjectives—only meaning and story logic

---

#### Agent 2: Scene Decomposition Agent
**Purpose**: Translate story beats into physical reality

- Defines what physically exists
- Who is present and where
- What actions occur
- Start state → End state changes

**Rules**: No camera language, no lighting, no stylistic language—only objective facts

---

#### Agent 3: Character Identity Agent
**Purpose**: Create absolute identity anchors (IMMUTABLE)

- Locks face, age, ethnicity, bone structure
- Locks wardrobe, hair, posture
- Creates reusable identity blocks

**Rules**: Characters are immutable once locked. Future scenes MUST reuse identity blocks verbatim.

---

#### Agent 4: Spatial & Temporal Continuity Agent
**Purpose**: Prevent AI drift and jump cuts

- Enforces same-location logic
- Prevents teleportation and pose snapping
- Defines allowed vs prohibited changes
- Ensures end frame feels like next second of start frame

**Rules**: Movement must be physically plausible. No wardrobe/lighting/weather changes unless specified.

---

#### Agent 5: Camera & Optics Agent
**Purpose**: Enforce photographic realism

- Selects real camera bodies (Sony FX6, Canon C70, etc.)
- Selects real lenses with focal lengths
- Defines depth of field
- Camera position relative to subjects

**Rules**: Documentary realism over cinematic framing. No impossible lenses. No drone shots unless grounded.

---

#### Agent 6: Lighting Physics Agent
**Purpose**: Ensure believable light behavior

- Identifies natural/practical light sources
- Defines directionality and color temperature
- Shadow behavior
- Light must come from something that exists in scene

**Rules**: No studio lighting unless justified. No dramatic clichés. Natural light only.

---

#### Agent 7: Composition & Observation Agent
**Purpose**: Remove "AI cinematic look"

- Enforces unstructured, asymmetric framing
- Observer-as-witness perspective
- Avoids rule-of-thirds and symmetry
- Embraces natural imperfection

**Rules**: No perfect composition. No centered subjects. Documentary style.

---

#### Agent 8: Motion & VFX Agent
**Purpose**: Handle controlled motion and overlays

- Defines subtle physical movement
- Start state → End state transitions
- VFX as non-destructive layers
- Ensures motion is plausible

**Rules**: No teleportation. No spectacle without narrative reason. Realistic physics.

---

#### Agent 9: Prompt Compiler Agent
**Purpose**: Merge all agents into final deterministic prompt

- Assembles start frame prompt
- Assembles end frame prompt
- Preserves all constraints
- Enforces anti-AI artifact rules

**Output**:
```
START FRAME: Full deterministic prompt with all specifications
END FRAME: Same as start + motion delta + continuity enforcement
```

**Anti-AI Enforcement Block (mandatory in every prompt)**:
```
No AI gloss. No plastic skin. No symmetry correction. No face drift.
No wardrobe drift. No film grain. No lens flares. No bokeh.
No post-processing. No stylized filters. RAW documentary photography.
Unmediated reality. Imperfect but real.
```

---

## Global Memory Rules

The compiler enforces these immutability constraints:

- ✅ Characters are immutable once defined
- ✅ Locations are immutable once defined
- ✅ Time-of-day is immutable per scene
- ✅ Wardrobe is immutable unless explicitly changed
- ✅ Facial identity NEVER changes
- ✅ Physical proportions NEVER drift
- ✅ Camera realism always overrides cinematic flair

---

## Usage

### 1. CLI Interface

```bash
# Create project
python -m studio.cinematic_compiler.cli create "My Film" --platform veo3

# Add scenes
python -m studio.cinematic_compiler.cli add-scene cin_abc123 \
  --description "Opening scene in coffee shop" \
  --duration 5.0

# Compile project
python -m studio.cinematic_compiler.cli compile cin_abc123

# Export prompts
python -m studio.cinematic_compiler.cli export cin_abc123 --format json

# Generate videos
python -m studio.cinematic_compiler.cli generate cin_abc123

# List all projects
python -m studio.cinematic_compiler.cli list

# Project info
python -m studio.cinematic_compiler.cli info cin_abc123
```

---

### 2. Python API

```python
from studio.cinematic_compiler import CinematicCompiler

# Initialize
compiler = CinematicCompiler()

# Create project
project = compiler.create_project(
    title="My Cinematic Film",
    target_platform="veo3",
    visual_style_rules="Noir aesthetic, high contrast"
)

# Add scenes
scene1 = compiler.add_scene(project,
    scene_description="Detective enters dark office",
    duration_seconds=5.0
)

# Compile
compiled_project = compiler.compile_project(project)

# Get prompts
prompts = compiler.get_compiled_prompts(compiled_project)

# Export for Veo 3
veo_requests = compiler.export_for_veo(compiled_project)

# Generate videos
from studio.cinematic_compiler.video_generator import CinematicVideoGenerator

generator = CinematicVideoGenerator()
results = generator.generate_project_full(compiled_project)
```

---

### 3. REST API

**Base URL**: `http://localhost:5000/api/cinematic`

#### Create Project
```bash
POST /projects
{
  "title": "My Film",
  "target_platform": "veo3",
  "visual_style_rules": "Documentary realism"
}
```

#### Add Scene
```bash
POST /projects/{project_id}/scenes
{
  "description": "Opening scene",
  "duration_seconds": 5.0
}
```

#### Compile Project
```bash
POST /projects/{project_id}/compile
```

#### Get Prompts
```bash
GET /projects/{project_id}/prompts
```

#### Generate Videos
```bash
POST /projects/{project_id}/generate
```

#### Export for Veo 3
```bash
GET /projects/{project_id}/export/veo
```

---

### 4. Integration with Studio Pipeline

The compiler can be integrated into the existing studio agent pipeline:

```python
from studio.agents.cinematic_compiler_agent import CinematicCompilerAgent

# In orchestrator, add between FrameAgent and VideoAgent:
compiler_agent = CinematicCompilerAgent()

# Enhance clips
enhanced_clips = await compiler_agent.enhance_clips(job, clips)
```

This replaces the FrameAgent's output with compiler-generated prompts while preserving the existing pipeline structure.

---

## State Persistence

All project state is stored in:
```
data/cinematic_projects/{project_id}.json
```

Each project file contains:
- Global character identities (locked)
- Global location definitions
- Visual style rules
- All scenes with full compilation data
- Start/end frame prompts for each scene

State persists across:
- Python sessions
- API server restarts
- Different execution environments

---

## Data Schemas

### CinematicProject
```python
{
  "project_id": str,
  "title": str,
  "created_at": datetime,
  "global_characters": Dict[str, CharacterIdentity],
  "global_locations": Dict[str, str],
  "visual_style_rules": str,
  "scenes": List[CinematicScene],
  "current_stage": CompilerStage,
  "compilation_complete": bool,
  "target_platform": str,  # "veo3", "nanoBanana", "both"
  "target_resolution": str,
  "target_fps": int
}
```

### CinematicScene
```python
{
  "scene_id": str,
  "sequence_number": int,
  "narrative": NarrativeBeat,
  "physical_reality": PhysicalReality,
  "character_identities": List[CharacterIdentity],
  "spatial_state": SpatialState,
  "camera": CameraSpec,
  "lighting": LightingPhysics,
  "composition": CompositionRules,
  "motion": MotionDelta,
  "start_frame_prompt": CompiledPrompt,
  "end_frame_prompt": CompiledPrompt,
  "duration_seconds": float,
  "locked": bool
}
```

### CharacterIdentity (IMMUTABLE)
```python
{
  "character_id": str,
  "canonical_name": str,
  "age": str,
  "ethnicity": str,
  "bone_structure": str,
  "face_shape": str,
  "distinctive_features": str,
  "hair_description": str,
  "facial_hair": str,
  "body_type": str,
  "height_relative": str,
  "posture_tendencies": str,
  "wardrobe": str,
  "accessories": str,
  "reference_image_url": Optional[str],
  "identity_locked": bool
}
```

---

## Output Format

Each compiled scene produces two prompts:

### START FRAME PROMPT
```
[Character identity blocks] [Environment] [Camera spec] [Lighting]
[Composition] [Anti-AI rules]
```

### END FRAME PROMPT
```
[Same character identities] (exact same appearance as start frame)
[Same environment] (exact same location and conditions)
[Camera spec] [Lighting] [Composition]
Motion: [Subtle physical movement description]
[Anti-AI rules]
```

**Example**:
```
START: Sarah Martinez, 32 year old Hispanic, angular bone structure,
oval face, distinctive scar on left eyebrow. Long dark hair in ponytail.
Clean facial features. Athletic build, average height, confident upright
posture. Wearing: black leather jacket over white t-shirt, blue jeans.
Silver watch. Modern coffee shop interior, exposed brick walls,
afternoon light streaming through large windows. Time: afternoon.
Weather: clear. Shot on Sony FX6 with Sony 24-70mm f/2.8 GM II at 35mm,
f/2.8. Camera positioned slightly offset, eye-level, medium from subject.
Medium depth of field, focus on subject's eyes. Documentary style,
handheld realism. Lighting: natural afternoon light from left
(5200K slightly warm), with ambient interior lighting. Shadows cast to right,
soft, medium density. Ambient light medium, neutral tone. Natural lighting
only, no studio setup. Unstructured framing, asymmetric balance, witness
perspective. Avoid centered composition, avoid symmetry, embrace natural
imperfection. No AI gloss. No plastic skin. No symmetry correction.
No face drift. No wardrobe drift. No film grain. No lens flares.
No bokeh. No post-processing. No stylized filters. RAW documentary
photography. Unmediated reality. Imperfect but real.

END: [Same as START] Motion: Sarah slowly turns head from looking
down at table to making eye contact with camera, slight smile beginning
to form at corner of mouth. Subtle shift in posture from neutral to
slightly leaning forward.
```

---

## API Integration

### Veo 3 (Google)
Export format:
```json
{
  "prompt": "[END FRAME PROMPT]",
  "reference_image_prompt": "[START FRAME PROMPT]",
  "duration_seconds": 5.0,
  "resolution": "1920x1080",
  "fps": 24
}
```

### Nano Banana Pro
Export format:
```json
[
  {
    "frame_type": "start",
    "prompt": "[START FRAME PROMPT]",
    "resolution": "1920x1080"
  },
  {
    "frame_type": "end",
    "prompt": "[END FRAME PROMPT]",
    "resolution": "1920x1080"
  }
]
```

---

## Directory Structure

```
studio/cinematic_compiler/
├── __init__.py              # Package exports
├── README.md                # This file
├── engine.py                # Core compiler orchestrator
├── schemas.py               # Data structure definitions
├── state_manager.py         # Persistent storage
├── video_generator.py       # Veo/Nano Banana integration
├── cli.py                   # Command-line interface
└── agents/                  # 9 internal agents
    ├── __init__.py
    ├── base_agent.py
    ├── idea_narrative_agent.py
    ├── scene_decomposition_agent.py
    ├── character_identity_agent.py
    ├── spatial_temporal_agent.py
    ├── camera_optics_agent.py
    ├── lighting_physics_agent.py
    ├── composition_agent.py
    ├── motion_vfx_agent.py
    └── prompt_compiler_agent.py

data/cinematic_projects/     # Persistent project storage
data/exports/                # Exported prompt files
```

---

## Key Principles

1. **COMPILER, NOT WRITER**
   - Structure first, creativity constrained
   - Each transformation is explicit and traceable
   - No vague or ambiguous outputs

2. **IMMUTABILITY**
   - Once locked, identity never changes
   - Characters maintain consistency across all scenes
   - Physical properties don't drift

3. **ANTI-AI ENFORCEMENT**
   - Removes plastic skin, AI gloss, perfect symmetry
   - Forces documentary realism
   - Natural imperfection is preserved

4. **PERSISTENCE**
   - State survives across sessions
   - Can resume projects at any time
   - Full audit trail of all decisions

5. **DETERMINISM**
   - Same inputs → same outputs
   - No randomness in compilation
   - Reproducible results

---

## Limitations & Future Work

**Current Limitations**:
- Agent implementations use placeholder logic (production would use Claude API for extraction)
- Character identity creation is simplified (needs full Claude integration)
- Scene decomposition requires manual input (needs narrative parsing)

**Future Enhancements**:
- Full Claude API integration for all agents
- Automatic scene analysis from script files
- Reference image ingestion for character locking
- Advanced continuity checking across scene boundaries
- LoRA model training integration for character consistency
- Multi-language support
- Video editing integration (timeline assembly)

---

## License

Part of the YouTube Automation system.

---

## Support

For issues or questions:
- Check `/studio/cinematic_compiler/examples/` for usage examples
- Review API documentation in `/studio/api/cinematic_routes.py`
- Consult main system README at project root
