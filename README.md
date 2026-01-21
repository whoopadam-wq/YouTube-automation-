# AI Content Automation Exoskeleton

**A reusable, settings-driven YouTube automation system for unlimited channels.**

## 🎯 Core Philosophy

**The automation is permanent. Channels are configurations.**

This system is built once and reused forever. Adding a new YouTube channel requires **ZERO code changes** — only configuration.

## ✨ Features

### Content Generation
- **Long-form videos** (8-12 minutes) with full narrative structure
- **Short-form videos** (30-90 seconds) optimized for YouTube Shorts
- **Persistent channel characters** (optional narrator/host)
- **Character-driven storytelling** with visual consistency
- **Automated scene planning** with cinematic direction

### Architecture
- ✅ **Modular pipeline** - Script → Characters → Scenes → Media → Assembly
- ✅ **API-agnostic** - Swap providers via configuration
- ✅ **Async orchestration** - Parallel generation for speed
- ✅ **Cost tracking** - Budget caps per channel and globally
- ✅ **State management** - SQLite-backed pipeline tracking
- ✅ **Scheduler** - Per-channel automated scheduling

### Supported APIs
- **Text Generation**: Anthropic Claude, OpenAI GPT-4
- **Image Generation**: Replicate (SDXL), OpenAI DALL-E 3
- **Video Generation**: Replicate (Stable Video Diffusion), Runway ML
- **Voice Synthesis**: ElevenLabs, OpenAI TTS

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd YouTube-automation-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required API keys:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (for script generation)
- `REPLICATE_API_TOKEN` (for image/video generation)
- `ELEVENLABS_API_KEY` (for voice synthesis)

### 3. Configure Your First Channel

Edit `config/channels.yaml` and customize the example channel or add your own:

```yaml
channels:
  - channel_id: "my_channel"
    channel_name: "My Awesome Channel"
    youtube_channel_id: "UCxxxxxxxxxxxxxxxxxx"

    niche: "technology"
    topic: "AI and machine learning breakthroughs"

    base_prompt: |
      Create engaging content about cutting-edge AI developments.
      Focus on practical applications and real-world impact.

    tone_style_modifiers:
      - "educational"
      - "enthusiastic"
      - "accessible"

    pacing_style: "fast"
    visual_style: "clean"

    use_channel_character: true
    channel_character:
      name: "Alex"
      visual_description: "Tech enthusiast in modern office, casual style"
      personality: "energetic, knowledgeable, friendly"
      voice_style: "clear, upbeat, conversational"

    long_form_enabled: true
    shorts_enabled: true
    shorts_per_day: 3
    target_long_duration: 10

    upload_timezone: "America/New_York"
    upload_schedule_long:
      - time: "18:00"
        days: ["monday", "wednesday", "friday"]

    api_cost_cap_per_day: 15.00
    status: "active"
```

### 4. Generate Content

```bash
# Generate a long-form video
python main.py generate-long my_channel

# Generate shorts
python main.py generate-shorts my_channel

# Start automated scheduler
python main.py schedule

# Check system status
python main.py status

# List all channels
python main.py list-channels
```

## 📁 Project Structure

```
YouTube-automation-/
├── config/
│   ├── channels.yaml           # Channel configurations
│   ├── system_config.yaml      # System settings
│   └── api_providers.yaml      # API provider configs
│
├── core/
│   ├── config_manager.py       # Configuration loader
│   ├── async_orchestrator.py  # Async API orchestration
│   ├── state_manager.py        # Pipeline state tracking
│   └── cost_tracker.py         # Cost management
│
├── modules/
│   ├── script_generator.py     # Script generation
│   ├── character_creator.py    # Character creation
│   ├── anchor_character.py     # Channel anchor character
│   ├── scene_planner.py        # Scene planning
│   ├── media_generator.py      # Image/video generation
│   ├── video_assembler.py      # Video assembly
│   ├── shorts_generator.py     # Shorts generation
│   └── scheduler.py            # Scheduling system
│
├── api_providers/
│   ├── base_provider.py        # Abstract base class
│   ├── anthropic_provider.py   # Claude integration
│   ├── openai_provider.py      # GPT/DALL-E integration
│   ├── replicate_provider.py   # Replicate integration
│   └── elevenlabs_provider.py  # ElevenLabs integration
│
├── workflows/
│   ├── long_form.py            # Long-form pipeline
│   └── short_form.py           # Short-form pipeline
│
├── data/
│   ├── channels/               # Channel-specific data
│   ├── assets/                 # Generated media
│   ├── database/               # SQLite database
│   └── output/                 # Final videos
│
└── main.py                     # Main entry point
```

## 🎬 Content Pipeline

### Long-Form Workflow

1. **Script Generation**
   - Uses LLM to create structured script
   - Includes narration, emotional beats, scene descriptions

2. **Character Creation**
   - Extracts characters from script
   - Generates consistent reference images

3. **Anchor Character** (Optional)
   - Persistent channel narrator/host
   - Created once, reused forever

4. **Scene Planning**
   - Detailed cinematography for each scene
   - Camera angles, lighting, motion planning

5. **Media Generation**
   - Parallel image generation (start frames)
   - Parallel video generation (image-to-video)

6. **Audio Generation**
   - Voice synthesis for narration
   - Background music (optional)

7. **Video Assembly**
   - Stitches scenes with FFmpeg
   - Adds narration and music
   - Final rendering

### Short-Form Workflow

1. **Script Generation** (with powerful hooks)
2. **Simplified Scene Planning** (3-5 scenes)
3. **Media Generation** (parallel)
4. **Assembly & Optimization** (9:16 aspect ratio)

## 💰 Cost Management

### Budget Controls

- **Per-channel daily caps** (configurable)
- **Global daily/monthly caps**
- **Automatic pause** at budget limit
- **Cost tracking** by category

### Cost Estimates

Typical costs per video:
- **Long-form (10 min)**: $10-15
  - Script: $0.05
  - Characters: $0.50
  - Images (30 scenes): $3.00
  - Videos (30 scenes): $60.00 (or $3-6 with optimized providers)
  - Voice: $0.15

- **Short-form (60 sec)**: $3-5
  - Script: $0.05
  - Images (3 scenes): $0.30
  - Videos (3 scenes): $6.00
  - Voice: $0.05

**Note**: Actual costs vary by provider and settings.

## ⚙️ Configuration Deep Dive

### Adding a New Channel

1. Open `config/channels.yaml`
2. Copy an existing channel block
3. Customize all fields
4. Set `status: "active"`
5. Run `python main.py status` to verify

**No code changes required!**

### Switching API Providers

Edit `config/api_providers.yaml`:

```yaml
providers:
  image_generation:
    primary: "replicate"  # Change to "openai" for DALL-E
    fallback: "openai"
```

### Adjusting Quality vs. Cost

Edit `config/system_config.yaml`:

```yaml
generation_defaults:
  image_generation:
    quality: "high"  # Change to "standard" for lower cost

  video_generation:
    fps: 30  # Reduce to 24 for lower cost
```

## 🔄 Async Orchestration

The system uses a universal async pattern for all API calls:

```python
# Submit task → Poll until complete → Return result
task = await orchestrator.submit_and_wait(
    submit_func=lambda: provider.submit_async(...),
    poll_func=lambda task_id: provider.poll_status(task_id),
    provider="replicate",
    task_type="video_gen"
)
```

All image/video generation happens in **parallel** for maximum speed.

## 📊 Monitoring

### View Status

```bash
python main.py status
```

Shows:
- Active channels
- Today's costs per channel
- Budget alerts
- Next scheduled runs

### Database

All pipeline state is stored in SQLite:
- `data/database/automation.db`

Query examples:
```sql
-- View all videos
SELECT * FROM videos;

-- View pipeline stages
SELECT * FROM pipeline_stages WHERE video_id = 'xxx';

-- View costs
SELECT * FROM costs WHERE channel_id = 'xxx';
```

## 🎨 Customization

### Visual Styles

Available styles (configurable per channel):
- `gritty` - Dark, moody, film noir
- `clean` - Bright, minimalist, modern
- `dramatic` - Cinematic, epic
- `minimal` - Simple, focused
- `vibrant` - Colorful, energetic

### Pacing Styles

- `cinematic` - Slow, deliberate
- `fast` - Quick cuts, high energy
- `documentary` - Medium, informative
- `casual` - Relaxed, conversational

## 🛠️ Troubleshooting

### "API key not found"
- Check `.env` file exists
- Verify key format in `.env`
- Restart application after editing `.env`

### "Budget exceeded"
- Check `python main.py status` for costs
- Adjust `api_cost_cap_per_day` in channel config
- Wait for daily reset (midnight UTC)

### "FFmpeg not found"
- Install FFmpeg: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)
- Ensure FFmpeg is in system PATH

### Generation fails
- Check API keys are valid
- Verify sufficient API credits
- Check logs in `data/logs/`
- Test with a single channel first

## 🚧 Future Enhancements

- [ ] Audio-to-video for anchor characters (HeyGen, D-ID)
- [ ] YouTube upload automation
- [ ] Multi-platform support (TikTok, Instagram)
- [ ] Advanced analytics and A/B testing
- [ ] Background music library integration
- [ ] Thumbnail generation
- [ ] SEO optimization tools

## 📄 License

MIT License - Use freely for personal or commercial projects.

## 🤝 Contributing

This is a production automation system. Contributions should focus on:
- New API provider integrations
- Performance optimizations
- Cost reduction strategies
- Quality improvements

## ⚠️ Important Notes

### Monetization Safety
- Ensure generated content complies with YouTube policies
- Use original characters and scenarios
- Respect copyright in prompts
- Enable content filtering in config

### API Costs
- Monitor costs daily via `python main.py status`
- Start with low daily caps during testing
- Actual costs vary by provider pricing
- Budget for approximately $10-15 per long-form video

### Rate Limits
- Configured per provider in `api_providers.yaml`
- System respects provider rate limits
- Use async orchestration for parallel generation

## 📞 Support

For issues or questions:
1. Check existing documentation
2. Review configuration files
3. Check API provider status
4. Review logs in `data/logs/`

---

**Built with**: Python 3.10+, Anthropic Claude, OpenAI, Replicate, ElevenLabs, FFmpeg

**Architecture**: Modular, API-agnostic, settings-driven, production-ready
