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

        self.base_url = "https://api.kie.ai/api/v1"
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
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Nano Banana Pro
        Fast, high-quality image generation
        Returns task info for async job
        """
        payload = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format
            }
        }

        if callback_url:
            payload["callBackUrl"] = callback_url

        response = requests.post(
            f"{self.base_url}/jobs/createTask",
            headers=self.headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            raise Exception(f"Nano Banana Pro failed: {response.status_code} - {response.text}")

        return response.json()

    def generate_image_nano_banana_pro_wait(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
        max_wait: int = 300
    ) -> str:
        """
        Generate image using Nano Banana Pro and wait for completion
        Returns image URL
        """
        result = self.generate_image_nano_banana_pro(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format
        )

        task_id = result.get("taskId") or result.get("task_id") or result.get("jobId")
        if not task_id:
            # If no task_id, it might be a direct response with URL
            return result.get("image_url") or result.get("url") or result.get("output_url") or ""

        print(f"   Nano Banana Pro task submitted: {task_id}")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status_data = self.poll_video_status(task_id)  # Uses same job polling endpoint
            status = status_data.get("status")

            if status == "completed":
                image_url = status_data.get("image_url") or status_data.get("url") or status_data.get("output_url") or status_data.get("imageUrl")
                print(f"   ✅ Nano Banana Pro complete: {image_url}")
                return image_url

            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                raise Exception(f"Nano Banana Pro failed: {error}")

            # Wait before next poll
            time.sleep(5)

        raise TimeoutError(f"Nano Banana Pro generation timed out after {max_wait}s")

    # ========================================================================
    # VIDEO GENERATION
    # ========================================================================

    def generate_video_veo3(
        self,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        aspect_ratio: str = "16:9",
        watermark: Optional[str] = None,
        callback_url: Optional[str] = None,
        seeds: Optional[int] = None,
        enable_fallback: bool = False,
        enable_translation: bool = True,
        generation_type: str = "REFERENCE_2_VIDEO"
    ) -> str:
        """
        Generate video using Veo 3
        Returns task_id for polling
        """
        payload = {
            "model": "veo3_fast",
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "enableFallback": enable_fallback,
            "enableTranslation": enable_translation,
            "generationType": generation_type
        }

        if image_urls:
            payload["imageUrls"] = image_urls
        if watermark:
            payload["watermark"] = watermark
        if callback_url:
            payload["callBackUrl"] = callback_url
        if seeds is not None:
            payload["seeds"] = seeds

        response = requests.post(
            f"{self.base_url}/veo/generate",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Veo 3 submission failed: {response.status_code} - {response.text}")

        data = response.json()
        return data.get("task_id") or data.get("jobId")

    def poll_video_status(self, task_id: str) -> Dict[str, Any]:
        """Poll video generation status"""
        response = requests.get(
            f"{self.base_url}/jobs/{task_id}",
            headers=self.headers,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Status poll failed: {response.status_code} - {response.text}")

        return response.json()

    async def generate_video_veo3_wait(
        self,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        aspect_ratio: str = "16:9",
        watermark: Optional[str] = None,
        seeds: Optional[int] = None,
        enable_fallback: bool = False,
        enable_translation: bool = True,
        generation_type: str = "REFERENCE_2_VIDEO",
        max_wait: int = 600
    ) -> str:
        """
        Generate video and wait for completion
        Returns video URL
        """
        task_id = self.generate_video_veo3(
            prompt=prompt,
            image_urls=image_urls,
            aspect_ratio=aspect_ratio,
            watermark=watermark,
            seeds=seeds,
            enable_fallback=enable_fallback,
            enable_translation=enable_translation,
            generation_type=generation_type
        )

        print(f"   Veo 3 task submitted: {task_id}")

        # Poll for completion
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status_data = self.poll_video_status(task_id)
            status = status_data.get("status")

            if status == "completed":
                video_url = status_data.get("video_url") or status_data.get("videoUrl") or status_data.get("output_url")
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
        Returns the image URL or task ID
        """
        if model == "nano-banana-pro":
            # Convert resolution to aspect_ratio and resolution format
            aspect_ratio = "1:1"
            res_str = "1K"

            if "x" in resolution:
                width, height = map(int, resolution.split("x"))
                if width == height:
                    aspect_ratio = "1:1"
                elif width > height:
                    aspect_ratio = f"{width // height}:1" if width % height == 0 else "16:9"
                else:
                    aspect_ratio = f"1:{height // width}" if height % width == 0 else "9:16"

                # Determine resolution level
                max_dim = max(width, height)
                if max_dim <= 1024:
                    res_str = "1K"
                elif max_dim <= 2048:
                    res_str = "2K"
                else:
                    res_str = "4K"

            # Use the wait method to get the URL directly
            return self.generate_image_nano_banana_pro_wait(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                resolution=res_str,
                output_format=kwargs.get("output_format", "png"),
                max_wait=kwargs.get("max_wait", 300)
            )
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
        if model == "veo-3" or model == "veo3_fast":
            # Map resolution to aspect ratio for Veo 3
            aspect_ratio = "16:9"  # Default
            if resolution == "1920x1080" or resolution == "16:9":
                aspect_ratio = "16:9"
            elif resolution == "1080x1920" or resolution == "9:16":
                aspect_ratio = "9:16"
            elif resolution == "1:1":
                aspect_ratio = "1:1"

            # Build image URLs list
            image_urls = []
            if reference_image_url:
                image_urls.append(reference_image_url)
            if kwargs.get("end_image_url"):
                image_urls.append(kwargs.get("end_image_url"))

            return await self.generate_video_veo3_wait(
                prompt=prompt,
                image_urls=image_urls if image_urls else None,
                aspect_ratio=aspect_ratio,
                watermark=kwargs.get("watermark"),
                seeds=kwargs.get("seeds"),
                enable_fallback=kwargs.get("enable_fallback", False),
                enable_translation=kwargs.get("enable_translation", True),
                generation_type=kwargs.get("generation_type", "REFERENCE_2_VIDEO" if image_urls else "TEXT_2_VIDEO"),
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
        voice: str = "Rachel",
        model: str = "elevenlabs/text-to-speech-turbo-2-5",
        speed: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        callback_url: Optional[str] = None
    ) -> str:
        """
        Generate audio/voice using ElevenLabs TTS via Kie AI
        Returns task_id for polling (synchronous call - polls automatically)
        """
        payload = {
            "model": model,
            "input": {
                "text": text,
                "voice": voice,
                "speed": speed,
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }

        if callback_url:
            payload["callBackUrl"] = callback_url

        response = requests.post(
            f"{self.base_url}/jobs/createTask",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Audio generation failed: {response.status_code} - {response.text}")

        data = response.json()
        task_id = data.get("task_id") or data.get("jobId")

        # Poll for completion (TTS is usually fast, max 60s wait)
        import time
        max_wait = 60
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_response = requests.get(
                f"{self.base_url}/jobs/{task_id}",
                headers=self.headers,
                timeout=30
            )

            if status_response.status_code != 200:
                raise Exception(f"Status check failed: {status_response.text}")

            status_data = status_response.json()
            status = status_data.get("status", "").lower()

            if status in ["completed", "success"]:
                # Extract audio URL from response
                audio_url = (
                    status_data.get("output", {}).get("audio_url") or
                    status_data.get("result", {}).get("audio_url") or
                    status_data.get("audioUrl")
                )
                if audio_url:
                    return audio_url
                raise Exception(f"Audio completed but no URL in response: {status_data}")

            elif status in ["failed", "error"]:
                error_msg = status_data.get("error") or status_data.get("message") or "Unknown error"
                raise Exception(f"Audio generation failed: {error_msg}")

            # Still processing, wait before polling again
            time.sleep(2)

        raise Exception(f"Audio generation timed out after {max_wait}s")

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
