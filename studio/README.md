# 🎬 AI Video Production Studio

**Professional video production with AI agents and timeline editing**

## What You Get

A complete production system that:
- Plans videos with sequential AI agents
- Generates assets with frame-level control
- Assembles videos with Remotion
- Provides timeline editing like CapCut
- Posts to YouTube, TikTok, Instagram

## Quick Start

```bash
# From the YouTube-automation- directory
cd studio

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
cp .env.example .env
# Edit .env and add your API keys

# Install Remotion (for video assembly)
cd remotion
npm install
cd ..

# Start the studio
python app.py
```

Open **http://localhost:3000**

## Architecture

### Sequential Agent Pipeline

1. **Script Agent** - Generates scene-by-scene breakdown
2. **Character Lock Agent** - Ensures character consistency
3. **Lighting Agent** - Designs lighting for mood
4. **Composition Agent** - Plans camera work
5. **Frame Agent** - Creates start/end frame prompts
6. **Video Agent** - Generates video clips
7. **Assembly Agent** - Renders final video with Remotion

**No skipping allowed** - Each agent runs in order.

### Two Modes

**AUTO Mode**: Run all agents automatically from start to finish

**REVIEW Mode**: Pause after each agent for human review and override

## Timeline Editor

Horizontal clip-based timeline like CapCut/Premiere:

- Video track with clips
- Audio track with narration
- Inspector panel showing:
  - Scene details
  - Character specs
  - Lighting settings
  - Composition settings
  - Frame prompts
- Click any clip to preview
- Regenerate individual stages
- Override agent decisions

## API Endpoints

### Jobs

```
GET  /api/jobs                      # List all jobs
POST /api/jobs                      # Create new job
GET  /api/jobs/:id                  # Get job details
POST /api/jobs/:id/start            # Start pipeline
POST /api/jobs/:id/continue         # Continue from current stage
POST /api/jobs/:id/regenerate/:stage # Regenerate a stage
```

### Clips

```
PATCH /api/jobs/:id/clips/:clip_id  # Update clip properties
```

### Posting

```
POST /api/jobs/:id/post             # Post to platforms
```

## Data Flow

```
ProductionJob
  ├── Global settings (style, tone, platform)
  ├── Global characters (locked across scenes)
  └── Clips[]
      ├── Script content
      ├── Characters (references to global)
      ├── LightingSpec
      ├── CompositionSpec
      ├── FrameSpec (start/end prompts)
      ├── Video URL
      └── Audio URL

→ Assembly Agent combines into final video
```

## Environment Variables

Required:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REPLICATE_API_TOKEN=r8_...
ELEVENLABS_API_KEY=...
```

Optional:
```
PORT=3000
STUDIO_MOCK_GENERATION=true  # Use mock generation for testing
STUDIO_MOCK_POSTING=true     # Use mock posting for testing
```

## Development

### Mock Mode

For testing without API costs:
```
export STUDIO_MOCK_GENERATION=true
export STUDIO_MOCK_POSTING=true
python app.py
```

Agents will return placeholder data instantly.

### Testing the Pipeline

```bash
# Create a sample job
curl -X POST http://localhost:3000/api/test/create-sample

# Or use the UI:
# Click "Create Sample Job (Test)" button on home page
```

## Platform Posting

### YouTube
- Requires OAuth2 setup
- Set `YOUTUBE_CLIENT_SECRETS` path
- Privacy: private, unlisted, public

### TikTok
- Requires developer account
- Set `TIKTOK_ACCESS_TOKEN`
- Automatically formats for 9:16

### Instagram
- Requires Facebook Business account
- Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_ACCOUNT_ID`
- Uploads as Reels

## Remotion Assembly

The Assembly Agent uses Remotion to:
- Sync video clips with audio narration
- Add caption overlays (for social platforms)
- Handle transitions (cut, fade, dissolve)
- Render multiple aspect ratios (16:9, 9:16, 1:1)

Remotion config: `studio/remotion/src/VideoComposition.tsx`

## File Structure

```
studio/
├── app.py                      # Main Flask application
├── orchestrator.py             # Agent orchestration engine
├── schemas.py                  # Data structures
├── requirements.txt
│
├── agents/
│   ├── script_agent.py
│   ├── character_lock_agent.py
│   ├── lighting_agent.py
│   ├── composition_agent.py
│   ├── frame_agent.py
│   ├── video_agent.py
│   └── assembly_agent.py
│
├── posting/
│   ├── youtube_poster.py
│   ├── tiktok_poster.py
│   ├── instagram_poster.py
│   └── post_manager.py
│
├── remotion/
│   ├── package.json
│   └── src/
│       └── VideoComposition.tsx
│
└── templates/
    ├── base.html
    ├── studio_home.html
    ├── timeline_editor.html
    └── new_production.html
```

## Troubleshooting

**Import errors**: Make sure you're in the project root, not the studio directory
```bash
cd /path/to/YouTube-automation-
python studio/app.py  # Not: cd studio && python app.py
```

**API key errors**: Check `.env` file or environment variables

**Remotion not found**: Run `npm install` in `studio/remotion/` directory

**Port in use**: Change PORT in environment: `PORT=8000 python app.py`

## Production Deployment

For production use:

1. **Disable mock mode**:
   ```
   export STUDIO_MOCK_GENERATION=false
   export STUDIO_MOCK_POSTING=false
   ```

2. **Use production server**:
   ```
   gunicorn -w 4 -b 0.0.0.0:3000 studio.app:app
   ```

3. **Set up API keys** for all providers

4. **Configure platform credentials** (YouTube OAuth, TikTok token, Instagram token)

## License

MIT

## Support

Issues? Questions? Open an issue on GitHub.
