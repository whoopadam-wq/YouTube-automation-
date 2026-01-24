"""
Kie.ai Provider Integration
Universal AI provider aggregator with support for all kie.ai tools
"""
import os
import requests
import time
from typing import Dict, Any, Optional, List


class KieAIProvider:
    """
    Kie.ai provider for accessing multiple AI models through one API
    Supports: Nano Banana Pro (images), Veo 3 (videos), and many more
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('KIEAI_API_KEY')
        if not self.api_key:
            raise ValueError("KIEAI_API_KEY not set")

        self.base_url = "https://api.kie.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    # ========================================================================
    # IMAGE GENERATION
    # ========================================================================

    def generate_image_nano_banana_pro(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 20,
        guidance_scale: float = 3.5
    ) -> Dict[str, Any]:
        """
        Generate image using Nano Banana Pro
        Fast, high-quality image generation
        """
        payload = {
            "model": "nano-banana-pro",
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale
        }

        response = requests.post(
            f"{self.base_url}/images/generate",
            headers=self.headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f"Nano Banana Pro failed: {response.text}")

        return response.json()

    # ========================================================================
    # VIDEO GENERATION
    # ========================================================================

    def generate_video_veo3(
        self,
        prompt: str,
        start_image_url: Optional[str] = None,
        end_image_url: Optional[str] = None,
        duration: float = 5.0,
        aspect_ratio: str = "16:9"
    ) -> str:
        """
        Generate video using Veo 3
        Returns task_id for polling
        """
        payload = {
            "model": "veo-3",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }

        if start_image_url:
            payload["start_image_url"] = start_image_url
        if end_image_url:
            payload["end_image_url"] = end_image_url

        response = requests.post(
            f"{self.base_url}/videos/generate",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Veo 3 submission failed: {response.text}")

        data = response.json()
        return data.get("task_id")

    def poll_video_status(self, task_id: str) -> Dict[str, Any]:
        """Poll video generation status"""
        response = requests.get(
            f"{self.base_url}/videos/status/{task_id}",
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Status poll failed: {response.text}")

        return response.json()

    async def generate_video_veo3_wait(
        self,
        prompt: str,
        start_image_url: Optional[str] = None,
        end_image_url: Optional[str] = None,
        duration: float = 5.0,
        aspect_ratio: str = "16:9",
        max_wait: int = 600
    ) -> str:
        """
        Generate video and wait for completion
        Returns video URL
        """
        task_id = self.generate_video_veo3(
            prompt=prompt,
            start_image_url=start_image_url,
            end_image_url=end_image_url,
            duration=duration,
            aspect_ratio=aspect_ratio
        )

        print(f"   Veo 3 task submitted: {task_id}")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status_data = self.poll_video_status(task_id)
            status = status_data.get("status")

            if status == "completed":
                video_url = status_data.get("video_url")
                print(f"   ✅ Veo 3 complete: {video_url}")
                return video_url

            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                raise Exception(f"Veo 3 failed: {error}")

            # Wait before next poll
            time.sleep(10)

        raise TimeoutError(f"Veo 3 generation timed out after {max_wait}s")

    # ========================================================================
    # GENERIC WRAPPER METHODS (for backward compatibility)
    # ========================================================================

    def generate_image(
        self,
        prompt: str,
        model: str = "nano-banana-pro",
        resolution: str = "1024x1024",
        **kwargs
    ) -> str:
        """
        Generic image generation wrapper
        Automatically routes to the correct model-specific method
        Returns the image URL
        """
        if model == "nano-banana-pro":
            # Parse resolution string like "1024x1024" or "1920x1080"
            if "x" in resolution:
                width, height = map(int, resolution.split("x"))
            else:
                width = height = 1024

            result = self.generate_image_nano_banana_pro(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=kwargs.get("num_inference_steps", 20),
                guidance_scale=kwargs.get("guidance_scale", 3.5)
            )

            # Extract image URL from response
            # The response should have an 'image_url' or 'url' field
            return result.get("image_url") or result.get("url") or result.get("output_url", "")
        else:
            raise ValueError(f"Unsupported image model: {model}")

    async def generate_video(
        self,
        prompt: str,
        model: str = "veo-3",
        duration: float = 5.0,
        resolution: str = "1920x1080",
        fps: int = 30,
        reference_image_url: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generic video generation wrapper
        Automatically routes to the correct model-specific method
        Returns video URL after waiting for completion
        """
        if model == "veo-3":
            # Map resolution to aspect ratio for Veo 3
            aspect_ratio = "16:9"  # Default
            if resolution == "1920x1080" or resolution == "16:9":
                aspect_ratio = "16:9"
            elif resolution == "1080x1920" or resolution == "9:16":
                aspect_ratio = "9:16"
            elif resolution == "1:1":
                aspect_ratio = "1:1"

            return await self.generate_video_veo3_wait(
                prompt=prompt,
                start_image_url=reference_image_url,
                end_image_url=kwargs.get("end_image_url"),
                duration=duration,
                aspect_ratio=aspect_ratio,
                max_wait=kwargs.get("max_wait", 600)
            )
        else:
            raise ValueError(f"Unsupported video model: {model}")

    # ========================================================================
    # TEXT GENERATION
    # ========================================================================

    def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using various LLMs available on kie.ai
        Supports: GPT-4, Claude, Gemini, Llama, etc.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = requests.post(
            f"{self.base_url}/text/generate",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Text generation failed: {response.text}")

        data = response.json()
        return data.get("text", "")

    # ========================================================================
    # AUDIO GENERATION
    # ========================================================================

    def generate_audio(
        self,
        text: str,
        voice_id: str = "default",
        model: str = "elevenlabs"
    ) -> str:
        """
        Generate audio/voice using various TTS models
        Supports: ElevenLabs, Play.ht, etc.
        """
        payload = {
            "model": model,
            "text": text,
            "voice_id": voice_id
        }

        response = requests.post(
            f"{self.base_url}/audio/generate",
            headers=self.headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Audio generation failed: {response.text}")

        data = response.json()
        return data.get("audio_url", "")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def list_available_models(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all available models on kie.ai
        Category: 'image', 'video', 'text', 'audio', 'embedding', etc.
        """
        params = {}
        if category:
            params["category"] = category

        response = requests.get(
            f"{self.base_url}/models",
            headers=self.headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Failed to list models: {response.text}")

        return response.json().get("models", [])

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        response = requests.get(
            f"{self.base_url}/models/{model_name}",
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get model info: {response.text}")

        return response.json()

    # ========================================================================
    # EXTENSIBILITY - Easy plugin for new tools
    # ========================================================================

    def call_any_model(
        self,
        model_name: str,
        endpoint: str,
        payload: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Universal method to call any kie.ai model/tool
        Makes it easy to add new AI tools without code changes

        Example:
            provider.call_any_model(
                model_name="new-image-model",
                endpoint="/images/generate",
                payload={"prompt": "..."}
            )
        """
        url = f"{self.base_url}{endpoint}"

        if method.upper() == "POST":
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
        elif method.upper() == "GET":
            response = requests.get(
                url,
                headers=self.headers,
                params=payload,
                timeout=120
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code not in [200, 201]:
            raise Exception(f"API call failed: {response.text}")

        return response.json()

    def __repr__(self):
        return f"<KieAIProvider api_key={'***' + self.api_key[-4:] if self.api_key else 'None'}>"


# ============================================================================
# CONVENIENCE WRAPPER
# ============================================================================

class KieAIToolRegistry:
    """
    Registry for easily adding and managing new kie.ai tools
    Makes it trivial to integrate new models as they become available
    """

    def __init__(self, provider: KieAIProvider):
        self.provider = provider
        self.registered_tools = {}

    def register_tool(
        self,
        tool_name: str,
        endpoint: str,
        method: str = "POST",
        default_params: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new kie.ai tool for easy access

        Example:
            registry.register_tool(
                tool_name="image_upscaler",
                endpoint="/images/upscale",
                default_params={"scale": 2}
            )
        """
        self.registered_tools[tool_name] = {
            "endpoint": endpoint,
            "method": method,
            "default_params": default_params or {}
        }

    def use_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Use a registered tool"""
        if tool_name not in self.registered_tools:
            raise ValueError(f"Tool '{tool_name}' not registered")

        tool_config = self.registered_tools[tool_name]

        # Merge default params with provided params
        final_params = {**tool_config["default_params"], **params}

        return self.provider.call_any_model(
            model_name=tool_name,
            endpoint=tool_config["endpoint"],
            payload=final_params,
            method=tool_config["method"]
        )

    def list_registered_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.registered_tools.keys())
