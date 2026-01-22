# 🎬 AI Video Production Studio
**Production-grade automated video factory**

## Quick Start on MacBook

```bash
# Navigate to project
cd YouTube-automation-

# Install dependencies
pip install -r studio/requirements.txt

# Set up API keys (copy and edit)
cp studio/.env.example studio/.env
# Edit studio/.env and add your API keys

# Optional: Install Remotion for video assembly
cd studio/remotion && npm install && cd ../..

# Start the studio (with mock mode enabled for testing)
python studio/app.py
```

Open: **http://localhost:3000**

That's it. No deploy complexity. Just works.

**Note**: Studio runs in MOCK mode by default (no API calls). To use real generation, edit `studio/app.py` and set `STUDIO_MOCK_GENERATION='false'`.

---

## What You Get

A complete video production studio:
- 📝 Script generation with scene breakdown
- 🎭 Character locking and consistency
- 💡 Lighting and composition agents
- 🎬 Frame-controlled video generation
- ✂️ Timeline editor with preview
- 📤 Multi-platform posting
- 🤖 Full agent orchestration

---

## Studio Architecture

```
Studio/
├── Agents (Sequential Pipeline)
│   ├── 1. Script Agent
│   ├── 2. Character Lock Agent
│   ├── 3. Lighting Agent
│   ├── 4. Composition Agent
│   ├── 5. Frame Agent
│   ├── 6. Video Agent
│   └── 7. Assembly Agent
│
├── Editor
│   ├── Timeline view
│   ├── Preview player
│   ├── Audio lanes
│   └── Export controls
│
├── Remotion Engine
│   ├── Scene assembly
│   ├── Audio sync
│   ├── Caption overlay
│   └── Multi-format render
│
└── Platform Posting
    ├── YouTube API
    ├── TikTok API
    ├── Instagram API
    └── Scheduling engine
```

---

## Run Locally (Simple)

### Option 1: Development Server
```bash
python studio/app.py
```

### Option 2: Production Mode
```bash
gunicorn studio.app:app -w 4 -b 0.0.0.0:3000
```

### Option 3: Docker (Optional)
```bash
docker-compose up
```

---

## System Requirements

- Python 3.10+
- Node.js 18+ (for Remotion)
- FFmpeg
- 8GB RAM minimum

---

## What's Built

✅ **Complete Agent Orchestration**
- 7 sequential agents with Review/Auto modes
- ProductionOrchestrator manages entire pipeline
- No-skip enforcement

✅ **Timeline Editor UI**
- Horizontal clip timeline
- Preview player
- Inspector panel with all agent data
- Regenerate any stage
- Update clip properties

✅ **Remotion Integration**
- React-based video composition
- Audio sync and captions
- Multi-format rendering (16:9, 9:16, 1:1)
- Smooth transitions

✅ **Platform Posting**
- YouTube (OAuth2 ready)
- TikTok (API ready)
- Instagram Reels (API ready)
- Unified PostManager

✅ **Production Schemas**
- ProductionJob, SceneClip, CharacterSpec
- LightingSpec, CompositionSpec, FrameSpec
- Complete data flow from Script → Assembly

---

## Usage

### Create a Production

1. Click **"New Production"**
2. Enter title and topic
3. Choose platform (YouTube, TikTok, Instagram)
4. Set duration and style
5. Select mode (Auto or Review)
6. Click **"Start Production"**

### Timeline Editing

1. View clips in horizontal timeline
2. Click any clip to preview
3. Inspector shows all agent decisions
4. Regenerate stages if needed
5. Continue production when ready

### Post to Platforms

1. Wait for production to complete
2. Click **"Post to Platforms"**
3. Select platforms
4. Video uploads automatically

---

**Ready to use!** 🚀

See full documentation: `studio/README.md`
