# Cinematic Production Compiler Integration Guide

## Overview

This repository now includes a **deterministic multi-agent cinematic production compiler** integrated into the YouTube automation system.

The compiler generates high-fidelity, consistent video prompts for Veo 3 and Nano Banana APIs.

---

## What Was Added

### 1. Core Compiler System
**Location**: `studio/cinematic_compiler/`

A 9-agent sequential pipeline that compiles story ideas into deterministic video generation prompts:

```
Idea → Scene → Character → Space → Camera → Light → Composition → Motion → Prompt
```

**Key Features**:
- ✅ Persistent state across sessions
- ✅ Immutable character identities
- ✅ Anti-AI artifact enforcement
- ✅ Documentary realism with real camera specs
- ✅ Photographic lighting physics
- ✅ Strict continuity enforcement

**Documentation**: See `/studio/cinematic_compiler/README.md`

---

### 2. Integration Points

#### Option A: Standalone Usage
Use the compiler independently via CLI or Python API:

```bash
# CLI
python -m studio.cinematic_compiler.cli create "My Film" --platform veo3
python -m studio.cinematic_compiler.cli add-scene cin_abc123
python -m studio.cinematic_compiler.cli compile cin_abc123
python -m studio.cinematic_compiler.cli generate cin_abc123
```

```python
# Python API
from studio.cinematic_compiler import CinematicCompiler

compiler = CinematicCompiler()
project = compiler.create_project("My Film", target_platform="veo3")
scene = compiler.add_scene(project, scene_description="Opening scene")
compiler.compile_project(project)
```

#### Option B: Integrated with Studio Pipeline
**Location**: `studio/agents/cinematic_compiler_agent.py`

Add the CinematicCompilerAgent to the existing pipeline between FrameAgent and VideoAgent:

```python
from studio.agents.cinematic_compiler_agent import CinematicCompilerAgent

# In orchestrator
compiler_agent = CinematicCompilerAgent()
enhanced_clips = await compiler_agent.enhance_clips(job, clips)
```

This enhances the existing FrameAgent output with compiler-generated deterministic prompts.

#### Option C: REST API
**Location**: `studio/api/cinematic_routes.py`

Access via Flask API endpoints:

```bash
# Create project
POST http://localhost:5000/api/cinematic/projects
{
  "title": "My Film",
  "target_platform": "veo3"
}

# Compile
POST http://localhost:5000/api/cinematic/projects/{id}/compile

# Generate videos
POST http://localhost:5000/api/cinematic/projects/{id}/generate
```

To enable API routes, add to `studio/app.py`:

```python
from studio.api import cinematic_bp

app.register_blueprint(cinematic_bp)
```

---

### 3. Video Generation Integration
**Location**: `studio/cinematic_compiler/video_generator.py`

Integrates compiled prompts with:
- **Veo 3** (via kie.ai) for video generation
- **Nano Banana Pro** (via kie.ai) for frame image generation

Uses the existing `KieAIProvider` from `studio/providers/kieai_provider.py`.

---

### 4. State Persistence
**Location**: `data/cinematic_projects/`

All compiler projects are stored as JSON files with:
- Locked character identities
- Scene compilation data
- Start/end frame prompts
- Full compilation state

Projects persist across sessions and can be resumed at any time.

---

## System Architecture

### Existing Pipeline (Unchanged)
```
ScriptAgent → CharacterLockAgent → LightingAgent → CompositionAgent
  → FrameAgent → VideoAgent → AudioAgent → AssemblyAgent
```

### With Compiler Integration
```
ScriptAgent → CharacterLockAgent → LightingAgent → CompositionAgent
  → FrameAgent → [CinematicCompilerAgent] → VideoAgent → AudioAgent → AssemblyAgent
```

OR use compiler completely standalone:

```
[Standalone Cinematic Compiler] → Veo 3 / Nano Banana → Assembly
```

---

## Key Differences

### Traditional FrameAgent
- Single-pass prompt generation
- Limited continuity enforcement
- No persistent character memory
- Cinematic style (AI-glossy)

### Cinematic Compiler
- 9-agent sequential compilation
- Strict continuity locks
- Immutable character identities
- Documentary realism (anti-AI enforcement)
- Persistent state across sessions
- Real camera/lens specifications
- Natural lighting physics

---

## Data Flow

### Compiler → Video Generation

```
1. Create CinematicProject
   ↓
2. Add CinematicScenes
   ↓
3. Compile (9 agents process each scene)
   ↓
4. Export to Veo 3 format
   {
     "prompt": "[END FRAME COMPILED PROMPT]",
     "reference_image_prompt": "[START FRAME COMPILED PROMPT]",
     "duration_seconds": 5.0
   }
   ↓
5. Generate video via kie.ai provider
   ↓
6. Receive video URL
```

---

## Configuration

### Environment Variables

```bash
# Required for video generation
KIEAI_API_KEY=your_kieai_api_key

# Optional: Claude API for advanced agent processing
ANTHROPIC_API_KEY=your_anthropic_key
```

### Project Settings

```python
project = compiler.create_project(
    title="My Film",
    target_platform="veo3",           # or "nanoBanana" or "both"
    visual_style_rules="Noir aesthetic, high contrast"
)

# Configure per project
project.target_resolution = "1920x1080"  # or "1080x1920" for vertical
project.target_fps = 24                   # or 30
```

---

## Examples

### Example 1: Quick Standalone Project

```python
from studio.cinematic_compiler import CinematicCompiler
from studio.cinematic_compiler.video_generator import CinematicVideoGenerator

# Create compiler
compiler = CinematicCompiler()

# New project
project = compiler.create_project("Noir Detective Story", target_platform="veo3")

# Add scenes
scene1 = compiler.add_scene(project,
    scene_description="Detective enters dark office, rain visible through window",
    duration_seconds=5.0)

scene2 = compiler.add_scene(project,
    scene_description="Detective sits at desk, opens case file",
    duration_seconds=5.0)

# Compile
compiler.compile_project(project)

# Generate videos
generator = CinematicVideoGenerator()
results = generator.generate_project_full(project)

print(f"Generated {len(results)} videos")
for r in results:
    print(f"  Scene {r['sequence_number']}: {r['video_url']}")
```

### Example 2: Integration with Existing Pipeline

```python
from studio.orchestrator import Orchestrator
from studio.agents.cinematic_compiler_agent import CinematicCompilerAgent

# Add to orchestrator initialization
orchestrator = Orchestrator()
orchestrator.cinematic_compiler = CinematicCompilerAgent()

# In pipeline execution (after FrameAgent)
if use_cinematic_compiler:
    clips = await orchestrator.cinematic_compiler.enhance_clips(job, clips)

# Continue with VideoAgent as normal
```

### Example 3: Character Consistency Across Scenes

```python
# Compiler automatically locks character identities
project = compiler.create_project("Multi-Scene Story")

scene1 = compiler.add_scene(project, "Hero stands in doorway")
scene2 = compiler.add_scene(project, "Hero walks across room")
scene3 = compiler.add_scene(project, "Hero sits down")

# Compile - characters are locked after first scene
compiler.compile_project(project)

# All scenes will use EXACT same character identity
print(f"Locked characters: {len(project.global_characters)}")
for char_id, char in project.global_characters.items():
    print(f"  {char.canonical_name}: {char.wardrobe}")
```

---

## File Structure

```
YouTube-automation-/
├── studio/
│   ├── cinematic_compiler/          # NEW: Compiler system
│   │   ├── __init__.py
│   │   ├── README.md                # Detailed compiler docs
│   │   ├── engine.py                # Core orchestrator
│   │   ├── schemas.py               # Data structures
│   │   ├── state_manager.py         # Persistence
│   │   ├── video_generator.py       # Veo/Nano integration
│   │   ├── cli.py                   # CLI interface
│   │   └── agents/                  # 9 internal agents
│   │       ├── idea_narrative_agent.py
│   │       ├── scene_decomposition_agent.py
│   │       ├── character_identity_agent.py
│   │       ├── spatial_temporal_agent.py
│   │       ├── camera_optics_agent.py
│   │       ├── lighting_physics_agent.py
│   │       ├── composition_agent.py
│   │       ├── motion_vfx_agent.py
│   │       └── prompt_compiler_agent.py
│   │
│   ├── agents/
│   │   ├── cinematic_compiler_agent.py  # NEW: Pipeline integration
│   │   └── [existing agents...]
│   │
│   ├── api/                         # NEW: API module
│   │   ├── __init__.py
│   │   └── cinematic_routes.py      # REST API endpoints
│   │
│   └── [existing studio files...]
│
├── data/
│   ├── cinematic_projects/          # NEW: Compiler project storage
│   ├── exports/                     # NEW: Exported prompts
│   └── [existing data dirs...]
│
├── CINEMATIC_COMPILER.md            # This file
└── [existing files...]
```

---

## Migration Guide

### For Existing YouTube Automation Users

**No breaking changes**. The existing pipeline continues to work unchanged.

**To use the compiler**:

1. **Standalone**: Use CLI or Python API independently
2. **Integrated**: Add `CinematicCompilerAgent` to pipeline
3. **Hybrid**: Use compiler for some projects, existing pipeline for others

### Upgrading Existing Projects

The compiler is a separate system. Existing `ProductionJob` objects remain unchanged.

To use compiler with existing content:
1. Create new CinematicProject
2. Copy scene descriptions from existing job
3. Compile and generate with enhanced prompts

---

## Performance Considerations

### Compilation Speed
- **9 agents** process each scene sequentially
- Average: ~2-3 seconds per scene (with placeholder logic)
- With full Claude API integration: ~5-10 seconds per scene

### State Storage
- Each project: ~50-200 KB JSON file
- Scenes: ~10-30 KB each
- Character identities: ~2-5 KB each

### API Costs
- **Veo 3**: ~$0.10-0.50 per video depending on duration
- **Nano Banana**: ~$0.02-0.05 per image
- **Claude API** (if enabled): ~$0.001-0.01 per scene compilation

---

## Troubleshooting

### "Project not found"
State files are in `data/cinematic_projects/`. Ensure directory exists and has write permissions.

### "KIEAI_API_KEY not set"
Set environment variable:
```bash
export KIEAI_API_KEY=your_key
```

### "Scene missing required agent data"
Ensure all 9 agents have processed the scene. Check compilation logs.

### Character identity not consistent
Characters should be locked in `project.global_characters`. Verify with:
```python
print(project.global_characters)
```

---

## Next Steps

1. **Read detailed docs**: `/studio/cinematic_compiler/README.md`
2. **Try CLI**: `python -m studio.cinematic_compiler.cli create "Test"`
3. **Explore API**: Start Flask app and access `/api/cinematic/`
4. **Integrate**: Add to existing pipeline via `CinematicCompilerAgent`

---

## Contributing

To extend the compiler:
- Add new agents in `studio/cinematic_compiler/agents/`
- Follow `BaseCompilerAgent` pattern
- Update `engine.py` to include in pipeline
- Add to schemas if new data structures needed

---

## License

Part of YouTube Automation system. See main repository LICENSE.
