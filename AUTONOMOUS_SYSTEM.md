# AI Video Studio - Autonomous YouTube Automation System

## 🚀 Overview

A **fully autonomous, self-learning AI system** that manages your entire YouTube channel - from idea discovery to video production to performance optimization.

### What Makes This Special?

- **🧠 Self-Learning**: Gets smarter over time by analyzing what works
- **🔄 Autonomous**: Runs 24/7, constantly improving without manual intervention
- **📊 Channel-Aware**: Paste your YouTube channel URL and it immediately understands your style
- **🎯 Trend-Sensitive**: Monitors viral opportunities in real-time
- **💰 Cost-Aware**: Calculates exact production costs before generating
- **🎨 Professional Quality**: Uses state-of-the-art AI tools (Veo 3, Nano Banana Pro, ElevenLabs)

---

## 🎯 Quick Start

### 1. Integrate Your Channel

```python
from studio.channel_integration import quick_integrate

# Just paste your channel URL
channel = await quick_integrate("https://www.youtube.com/@YourChannel")

# The system now knows:
# - Your content style and tone
# - Your audience preferences
# - What topics work for you
# - Optimal video duration
# - Hook patterns that convert
```

### 2. Start Autonomous Learning

```python
from studio.autonomous_learning import get_learning_system

# Start the brain
learning_system = get_learning_system(channel_id=channel.channel_id)
await learning_system.start_continuous_learning()

# The system now:
# ✅ Monitors your channel performance 24/7
# ✅ Discovers trending topics automatically
# ✅ Analyzes what works and improves
# ✅ Updates strategies in real-time
```

### 3. Estimate Costs

```python
from studio.cost_estimator import compare_video_durations

# See costs for different video lengths
costs = compare_video_durations()

# Example output:
# 8 min:  $12.50 ($1.56/min)
# 15 min: $18.75 ($1.25/min) <- Best value
# 20 min: $23.00 ($1.15/min)
# 40 min: $38.50 ($0.96/min)
```

### 4. Generate Video

Production happens automatically with all the new intelligence!

---

## 🤖 New Agents & Systems

### 1. **Video Ideas Scraper Agent** 🔍
`studio/agents/ideas_scraper_agent.py`

**What it does:**
- Automatically discovers trending topics in your niche
- Uses Serper API to scrape viral content
- Analyzes channel style to find perfect topics
- Tracks history to avoid duplicate videos
- Ranks ideas by viral potential
- Saves to database for future use

**How to use:**
```python
from studio.agents.ideas_scraper_agent import IdeasScraperAgent

agent = IdeasScraperAgent(channel_id="YOUR_CHANNEL_ID")
ideas = await agent.discover_ideas(
    niche="tech reviews",
    num_ideas=10,
    include_trending=True
)

# Returns VideoIdea objects with:
# - topic
# - hook_angle
# - trending_score
# - research_notes
# - estimated_views
```

---

### 2. **YouTube Analytics Agent** 📊
`studio/agents/analytics_agent.py`

**What it does:**
- Studies your channel performance (CTR, AVD, views)
- Analyzes which hooks work best
- Identifies winning thumbnail patterns
- Tracks retention and drop-off points
- Discovers top-performing topics
- Finds optimal video duration
- Generates actionable recommendations

**How to use:**
```python
from studio.agents.analytics_agent import AnalyticsAgent

agent = AnalyticsAgent(channel_id="YOUR_CHANNEL_ID")
analysis = await agent.analyze_channel_performance(days_back=30)

# Returns:
# - Performance summary
# - Hook insights
# - Thumbnail insights
# - Retention patterns
# - Topic recommendations
# - Duration optimization
```

---

### 3. **Sound Engineer Agent** 🎵
`studio/agents/sound_engineer_agent.py`

**What it does:**
- Analyzes script emotional beats
- Generates background music with MusicGen
- Identifies moments needing sound effects
- Creates professional audio mix
- Balances narration, music, and SFX
- Auto-ducking for narration clarity

**How to use:**
```python
from studio.agents.sound_engineer_agent import SoundEngineerAgent

agent = SoundEngineerAgent()
audio_design = await agent.design_audio(job, clips)

# Returns:
# - audio_layers (narration, music, SFX, ambient)
# - mix_specifications (compression, EQ, ducking)
# - audio_direction
```

---

### 4. **Thumbnail Agent** 🖼️
`studio/agents/thumbnail_agent.py`

**What it does:**
- Generates CTR-optimized thumbnails with Nano Banana Pro
- Creates 3 A/B test variants
- Uses analytics insights to improve
- Applies proven techniques:
  - High contrast colors
  - Bold text overlays
  - Exaggerated expressions
  - Curiosity gaps
- Predicts CTR for each variant
- Learns from performance over time

**How to use:**
```python
from studio.agents.thumbnail_agent import ThumbnailAgent

agent = ThumbnailAgent()
thumbnails = await agent.generate_thumbnails(job, num_variants=3)

# Returns ThumbnailVariant objects:
# - image_url
# - design_strategy
# - text_overlay
# - predicted_ctr
```

---

### 5. **Remotion Motion Graphics Agent** ⚛️
`studio/agents/remotion_agent.py`

**What it does:**
- Analyzes scenes for visualization opportunities
- Generates Remotion/React/TypeScript code
- Creates Vox-style animated explainers:
  - Animated charts and graphs
  - Data visualizations
  - Text animations
  - Diagram overlays
- Exports complete Remotion projects
- Professional spring animations

**How to use:**
```python
from studio.agents.remotion_agent import RemotionAgent

agent = RemotionAgent()
motion_graphics = await agent.design_motion_graphics(job, clips)

# Returns:
# - motion_elements (code for each graphic)
# - main_composition (full Remotion project)
# - render_specs
# - Can export to filesystem for editing
```

---

### 6. **Cost Estimator** 💰
`studio/cost_estimator.py`

**What it does:**
- Calculates exact production costs
- Breaks down by component (LLM, images, video, audio, etc.)
- Researched pricing for all tools
- Compares different video durations
- Shows cost per minute
- Best value analysis

**How to use:**
```python
from studio.cost_estimator import CostEstimator

estimator = CostEstimator()
breakdown = estimator.estimate_production_cost(duration_minutes=15)

print(f"Total: ${breakdown.total_cost:.2f}")
print(f"Script: ${breakdown.script_generation:.2f}")
print(f"Images: ${breakdown.image_generation:.2f}")
print(f"Video: ${breakdown.video_generation:.2f}")

# Compare durations
comparison = estimator.compare_durations([8, 15, 20, 40])
```

**Typical Costs:**
- **8-minute video**: ~$12-15 ($1.50-1.88/min)
- **15-minute video**: ~$18-22 ($1.20-1.47/min) ⭐ Best value
- **20-minute video**: ~$23-28 ($1.15-1.40/min)
- **40-minute video**: ~$38-48 ($0.95-1.20/min)

---

### 7. **YouTube Channel Integration** 🔗
`studio/channel_integration.py`

**What it does:**
- Accepts channel URL in any format
- Extracts channel information via YouTube API
- Analyzes channel style, tone, content patterns
- Creates channel profile for all agents
- Automatically runs analytics
- Discovers initial video ideas
- Makes entire system channel-aware

**How to use:**
```python
from studio.channel_integration import YouTubeChannelIntegration

integration = YouTubeChannelIntegration()
channel = await integration.integrate_channel(
    "https://www.youtube.com/@YourChannel",
    auto_analyze=True,
    auto_discover_ideas=True
)

# Now all agents know:
# - Channel niche
# - Content tone
# - Target audience
# - Video duration preferences
# - Top-performing topics
```

---

### 8. **Autonomous Learning System** 🧠
`studio/autonomous_learning.py`

**What it does:**
- Runs continuously 24/7
- Monitors channel performance
- Discovers trends in real-time
- Analyzes what works and what doesn't
- Updates agent strategies automatically
- Tracks viral opportunities
- Meta-learning from patterns
- **Never stops improving**

**How to use:**
```python
from studio.autonomous_learning import get_learning_system

# Start the brain
system = get_learning_system(channel_id="YOUR_CHANNEL_ID")
await system.start_continuous_learning()

# It will:
# ✅ Check performance every 6 hours
# ✅ Monitor trends every 2 hours
# ✅ Discover meta-patterns
# ✅ Update strategies automatically
# ✅ Save high-impact learnings
# ✅ Generate reports

# Get learning report
report = system.get_learning_report()
print(report)
```

---

## 🎨 AI Tools Manager

### New LLMs Added

The tools manager now includes **all major LLMs** for script generation:

- **Claude 3.5 Sonnet** (active)
- **Claude 3 Opus**
- **GPT-4**
- **GPT-4 Turbo**
- **Gemini Pro**
- **Llama 3 70B**
- **Mistral Large**
- **Command R+**
- **Perplexity** (for research)

Access at: `/tools` in the web interface

---

## 📁 File Structure

```
studio/
├── agents/
│   ├── ideas_scraper_agent.py      # 🔍 Discovers trending topics
│   ├── analytics_agent.py          # 📊 Studies channel performance
│   ├── sound_engineer_agent.py     # 🎵 Adds music and SFX
│   ├── thumbnail_agent.py          # 🖼️ Generates CTR-optimized thumbnails
│   ├── remotion_agent.py           # ⚛️ Creates motion graphics
│   ├── script_agent.py             # 📝 Writes viral scripts
│   ├── character_lock_agent.py     # 👤 Character consistency
│   ├── lighting_agent.py           # 💡 Lighting design
│   ├── composition_agent.py        # 📐 Shot composition
│   ├── frame_agent.py              # 🖼️ Frame generation
│   ├── video_agent.py              # 🎬 Video generation
│   └── assembly_agent.py           # 🎞️ Final assembly
├── channel_integration.py          # 🔗 Channel connection system
├── autonomous_learning.py          # 🧠 Self-learning brain
├── cost_estimator.py              # 💰 Cost calculator
├── orchestrator.py                # 🎼 Production pipeline
├── schemas.py                     # 📋 Data structures
├── app.py                         # 🌐 Flask web app
└── templates/
    └── tools_manager.html         # 🎨 AI Tools UI
```

---

## 🚀 Complete Workflow

### The Autonomous Cycle

1. **Channel Integration** 🔗
   - User pastes YouTube channel URL
   - System analyzes channel style, tone, audience
   - Creates channel profile

2. **Autonomous Learning Starts** 🧠
   - Monitors channel performance 24/7
   - Analyzes what works (hooks, thumbnails, topics)
   - Discovers meta-patterns

3. **Trend Monitoring** 🔥
   - Scrapes trending topics every 2 hours
   - Identifies viral opportunities
   - Ranks by potential

4. **Idea Discovery** 💡
   - Automatically finds next video topic
   - Considers channel style
   - Avoids duplicates
   - Estimates views

5. **Cost Estimation** 💰
   - Calculates production cost
   - Shows breakdown by component
   - User approves budget

6. **Production** 🎬
   - **Script**: Optimized for retention with killer hooks
   - **Characters**: Consistent across scenes
   - **Lighting**: Professional cinematic lighting
   - **Composition**: Expert shot composition
   - **Frames**: Generated with Nano Banana Pro
   - **Video**: Animated with Veo 3
   - **Audio**: Narration with ElevenLabs
   - **Sound**: Music + SFX by Sound Engineer
   - **Motion Graphics**: Remotion overlays
   - **Thumbnails**: 3 CTR-optimized variants
   - **Assembly**: Final video composition

7. **Publishing** 📤
   - Upload to YouTube/TikTok/Instagram
   - Track initial performance

8. **Learning** 📈
   - Analyzes video performance
   - CTR, AVD, retention analysis
   - Updates strategies
   - Feeds back into system
   - **Gets smarter for next video**

---

## 🔧 Configuration

### Environment Variables

```bash
# Required for full functionality
ANTHROPIC_API_KEY=sk-ant-...           # For LLM agents
KIEAI_API_KEY=74ba78915402a077...      # For Veo 3, Nano Banana Pro, ElevenLabs
YOUTUBE_DATA_API_KEY=AIza...           # For channel integration & analytics
SERPER_API_KEY=...                     # For trend discovery (optional)

# Optional
STUDIO_MOCK_GENERATION=false           # Set to true for testing without costs
STUDIO_MOCK_POSTING=false              # Set to true to skip actual posting
```

### APIs Used

1. **Anthropic API** - Claude for script, analysis, code generation
2. **Kie.ai** - Unified API for:
   - Nano Banana Pro (images)
   - Veo 3 (videos)
   - ElevenLabs (voice)
   - MusicGen (music)
3. **YouTube Data API** - Channel info, analytics
4. **Serper API** - Web scraping for trends (optional)

---

## 💡 Example: Complete Autonomous Flow

```python
import asyncio
from studio.channel_integration import YouTubeChannelIntegration
from studio.autonomous_learning import get_learning_system
from studio.cost_estimator import quick_estimate

async def autonomous_youtube_channel():
    # Step 1: Connect channel
    print("🔗 Connecting to your channel...")
    integration = YouTubeChannelIntegration()
    channel = await integration.integrate_channel(
        "https://www.youtube.com/@YourChannel"
    )

    # Step 2: Start learning brain
    print("🧠 Starting autonomous learning...")
    learning = get_learning_system(channel_id=channel.channel_id)
    asyncio.create_task(learning.start_continuous_learning())

    # Step 3: Estimate costs
    print("💰 Calculating costs...")
    cost_15min = quick_estimate(15)
    print(f"15-min video will cost: ${cost_15min['total_cost_usd']:.2f}")

    # Step 4: System now runs autonomously!
    print("✅ System is now fully autonomous!")
    print("   - Monitoring performance 24/7")
    print("   - Discovering trending topics")
    print("   - Learning what works")
    print("   - Ready to produce videos")

# Run it
asyncio.run(autonomous_youtube_channel())
```

---

## 📊 What You Get

### Before (Manual Process)
- ❌ Manually research trending topics
- ❌ Guess what titles/thumbnails work
- ❌ Hope the video performs well
- ❌ No idea what's working or why
- ❌ Static strategies that don't improve

### After (Autonomous System)
- ✅ **Auto-discovers** trending topics in your niche
- ✅ **Analyzes** what hooks/thumbnails convert
- ✅ **Learns** from every video's performance
- ✅ **Adapts** strategies based on data
- ✅ **Improves** continuously without manual work
- ✅ **Predicts** costs before production
- ✅ **Generates** professional videos with motion graphics
- ✅ **Monitors** viral opportunities 24/7

---

## 🎯 Key Features

### 🧠 Intelligence
- Self-learning from channel analytics
- Pattern recognition across videos
- Meta-learning from learnings
- Trend prediction
- Performance forecasting

### 🔄 Automation
- Runs 24/7 without supervision
- Auto-discovers video ideas
- Auto-updates strategies
- Auto-monitors trends
- Auto-improves over time

### 📊 Analytics
- CTR analysis
- AVD (Average View Duration) tracking
- Hook effectiveness
- Thumbnail performance
- Topic success rates
- Retention patterns

### 🎨 Production
- Viral script generation
- Professional motion graphics (Remotion)
- CTR-optimized thumbnails
- Professional audio mixing
- Vox-style explainers
- High-quality video generation

### 💰 Cost Management
- Exact cost calculations
- Breakdown by component
- Duration comparisons
- Best value analysis
- Budget planning

---

## 🚀 Next Steps

1. **Set API Keys** in `.env` or `app.py`
2. **Integrate Your Channel** via `/tools` page or API
3. **Start Learning System** - it runs autonomously
4. **Review Discovered Ideas** in `data/video_ideas_history.json`
5. **Check Analytics** in `data/analytics_insights.json`
6. **Produce First Video** with all the intelligence
7. **Watch System Improve** as it learns from performance

---

## 📚 Documentation

- **Channel Integration**: See `studio/channel_integration.py` docstrings
- **Cost Estimator**: See `studio/cost_estimator.py` docstrings
- **Learning System**: See `studio/autonomous_learning.py` docstrings
- **Agents**: Each agent has detailed docstrings

---

## 🎉 Summary

You now have a **fully autonomous, self-learning YouTube automation system** that:

1. ✅ Understands your channel when you paste the URL
2. ✅ Constantly monitors trends and performance
3. ✅ Learns what works and improves over time
4. ✅ Generates professional videos with motion graphics
5. ✅ Optimizes for CTR, AVD, and viral potential
6. ✅ Calculates exact costs before production
7. ✅ Runs 24/7 without manual intervention
8. ✅ **Gets smarter every day**

**It's not just a tool - it's an AI team that never sleeps.** 🚀🧠

---

Built with ❤️ using Claude 3.5 Sonnet, Veo 3, Nano Banana Pro, ElevenLabs, and Remotion.
