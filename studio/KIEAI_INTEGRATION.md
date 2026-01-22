# Kie.ai Integration Guide

## Overview

The studio is fully integrated with **kie.ai** - a universal AI provider aggregator that gives you access to dozens of AI models through a single API.

Your API Key: `74ba78915402a077bb93b3cf140eb904`

## Current Integrations

### 🎨 Image Generation: Nano Banana Pro
- **Used by**: Frame Agent (generates start/end frames)
- **Why**: Fast, high-quality image generation with cinematic quality
- **Settings**: Configurable width, height, inference steps, guidance scale

### 🎬 Video Generation: Veo 3
- **Used by**: Video Agent (animates between frames)
- **Why**: Frame-controlled video generation with smooth motion
- **Capabilities**:
  - Start/end image control
  - Duration control (1-10 seconds)
  - Multi-aspect ratio (16:9, 9:16, 1:1)

### 🎙️ Voice Synthesis: ElevenLabs
- **Used by**: Audio Agent (generates narration)
- **Why**: Natural-sounding voice synthesis
- **Features**: Multiple voices, emotion control, pronunciation tuning

## Easy Tool Plugin System

### Using Any Kie.ai Tool

```python
from studio.providers.kieai_provider import KieAIProvider

# Initialize
provider = KieAIProvider(api_key="74ba78915402a077bb93b3cf140eb904")

# Use any tool with the universal method
result = provider.call_any_model(
    model_name="new-tool-name",
    endpoint="/category/action",
    payload={
        "param1": "value1",
        "param2": "value2"
    }
)
```

### Adding New Tools

**Option 1: Quick Use (No Code)**

Edit `studio/kieai_tools_config.yaml`:

```yaml
available_tools:
  your_new_tool:
    tool: tool-name
    endpoint: /category/action
    method: POST
    description: "What it does"
    default_params:
      param1: default_value
```

Then use via tool registry:

```python
from studio.providers.kieai_provider import KieAIToolRegistry

registry = KieAIToolRegistry(provider)
registry.register_tool(
    tool_name="your_new_tool",
    endpoint="/category/action"
)

result = registry.use_tool("your_new_tool", {"param": "value"})
```

**Option 2: Add Dedicated Method (Frequent Use)**

Edit `studio/providers/kieai_provider.py`:

```python
def your_new_method(self, param1, param2):
    """Description of what this does"""
    payload = {
        "param1": param1,
        "param2": param2
    }

    return self.call_any_model(
        model_name="tool-name",
        endpoint="/category/action",
        payload=payload
    )
```

## Available Tools on Kie.ai

### Image Tools
- ✅ **Nano Banana Pro** - Fast image generation (ACTIVE)
- **Real-ESRGAN** - Upscale images 2x-4x
- **Style Transfer** - Apply artistic styles
- **Rembg** - Background removal
- **Stable Diffusion Inpainting** - Edit image parts

### Video Tools
- ✅ **Veo 3** - Frame-controlled generation (ACTIVE)
- **Topaz Video AI** - Video upscaling
- **RIFE** - Frame interpolation (increase FPS)
- **Vid-Stab** - Video stabilization

### Audio Tools
- ✅ **ElevenLabs** - Voice synthesis (ACTIVE)
- **Audio Enhance** - Quality enhancement
- **Whisper** - Speech-to-text
- **MusicGen** - Background music generation

### 3D Tools
- **TripoSR** - Image to 3D
- **Shap-E** - Text to 3D

### Animation Tools
- **MediaPipe** - Motion capture
- **Wav2Lip** - Lip sync

See full list in `studio/kieai_tools_config.yaml`

## Integration Examples

### Example 1: Add Image Upscaling

```python
# In frame_agent.py or composition_agent.py
def _upscale_image(self, image_url: str) -> str:
    """Upscale image before using in video"""

    result = self.kieai_provider.call_any_model(
        model_name="real-esrgan",
        endpoint="/images/upscale",
        payload={
            "image_url": image_url,
            "scale": 2  # 2x upscale
        }
    )

    return result.get("upscaled_image_url")
```

### Example 2: Add Background Music

```python
# In assembly_agent.py
def _generate_background_music(self, mood: str, duration: float) -> str:
    """Generate background music for video"""

    result = self.kieai_provider.call_any_model(
        model_name="musicgen",
        endpoint="/audio/generate-music",
        payload={
            "duration": duration,
            "genre": "cinematic",
            "mood": mood
        }
    )

    return result.get("audio_url")
```

### Example 3: Add Video Upscaling

```python
# In video_agent.py
async def _upscale_video(self, video_url: str) -> str:
    """Upscale video to higher resolution"""

    result = self.kieai_provider.call_any_model(
        model_name="topaz-video-ai",
        endpoint="/videos/upscale",
        payload={
            "video_url": video_url,
            "target_resolution": "4k"
        }
    )

    return result.get("upscaled_video_url")
```

## Provider Configuration

All providers are configured in `studio/providers/kieai_provider.py`.

The provider handles:
- ✅ API authentication
- ✅ Request/response formatting
- ✅ Async task polling (for long-running jobs)
- ✅ Error handling and retries
- ✅ Timeout management

## Switching Providers

To use a different video model:

```python
# In video_agent.py, change:
video_url = await self.provider.generate_video_veo3_wait(...)

# To:
video_url = await self.provider.call_any_model(
    model_name="new-video-model",
    endpoint="/videos/generate",
    payload={...}
)
```

## Cost Management

Kie.ai provides unified billing across all models. Track usage:

```python
# List all models and their costs
models = provider.list_available_models()

for model in models:
    print(f"{model['name']}: ${model['cost_per_call']}")
```

## Troubleshooting

### API Key Issues
- Ensure `KIEAI_API_KEY` is set in `.env` or app.py
- Verify key is valid on kie.ai dashboard

### Tool Not Working
1. Check tool name in `kieai_tools_config.yaml`
2. Verify endpoint URL
3. Check payload format in kie.ai docs
4. Enable debug logging

### Slow Generation
- Some models take 30-60s (normal for video)
- Use async methods with polling
- Check `max_wait` timeout settings

## Resources

- **Kie.ai Dashboard**: https://kie.ai/dashboard
- **API Docs**: https://docs.kie.ai
- **Model List**: https://kie.ai/models
- **Pricing**: https://kie.ai/pricing

## Next Steps

1. **Explore Available Tools**: Check `kieai_tools_config.yaml` for full list
2. **Test in Mock Mode**: Studio defaults to mock mode for testing
3. **Enable Real Generation**: Set `STUDIO_MOCK_GENERATION=false` in app.py
4. **Monitor Usage**: Track API calls in kie.ai dashboard
5. **Optimize Costs**: Use appropriate models for each task

---

**Quick Reference**:
- Your API Key: `74ba78915402a077bb93b3cf140eb904`
- Provider File: `studio/providers/kieai_provider.py`
- Config File: `studio/kieai_tools_config.yaml`
- Integration: All agents support kie.ai natively
