"""
Remotion Motion Graphics Agent - Programmatic video composition expert
Generates Vox-style motion graphics and animated explainers using Remotion
"""
import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from studio.schemas import SceneClip, ProductionJob


class MotionGraphicElement:
    """Represents a motion graphic overlay element"""
    def __init__(
        self,
        element_id: str,
        element_type: str,  # "chart", "diagram", "text_animation", "transition", "data_viz"
        scene_number: int,
        start_time: float,
        duration: float,
        remotion_code: str,
        data: Optional[Dict] = None,
        description: str = ""
    ):
        self.element_id = element_id
        self.element_type = element_type
        self.scene_number = scene_number
        self.start_time = start_time
        self.duration = duration
        self.remotion_code = remotion_code
        self.data = data or {}
        self.description = description

    def to_dict(self):
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "scene_number": self.scene_number,
            "start_time": self.start_time,
            "duration": self.duration,
            "remotion_code": self.remotion_code,
            "data": self.data,
            "description": self.description
        }


class RemotionAgent:
    """
    Expert Remotion developer that:
    - Analyzes scenes to identify moments needing visual explanation
    - Generates Remotion JSX/TSX code for motion graphics
    - Creates Vox-style animated explainers:
      * Animated charts and graphs
      * Data visualizations
      * Text animations with timing
      * Diagram overlays
      * Smooth transitions
    - Knows Remotion API and React patterns
    - Exports render specifications
    - Professional animation principles (easing, timing, composition)
    """

    def __init__(self):
        # LLM for code generation and scene analysis
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not set - Remotion Agent will use basic mode")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20240620"

        # Remotion project setup
        self.remotion_version = "4.0"
        self.output_path = "data/remotion_compositions"

        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)

    async def design_motion_graphics(
        self,
        job: ProductionJob,
        clips: List[SceneClip]
    ) -> Dict[str, Any]:
        """
        Main method: Analyze scenes and generate motion graphics code

        Args:
            job: ProductionJob with video context
            clips: List of SceneClip objects with script

        Returns:
            Dict with motion_elements, remotion_composition, and render specs
        """
        print(f"⚛️  Remotion Agent: Designing motion graphics for '{job.title}'...")

        # Step 1: Analyze which scenes need motion graphics
        print(f"   🔍 Analyzing scenes for motion graphic opportunities...")
        graphic_opportunities = await self._analyze_scenes_for_graphics(job, clips)

        # Step 2: Generate Remotion code for each element
        print(f"   💻 Generating Remotion code...")
        motion_elements = []

        for opportunity in graphic_opportunities:
            element = await self._generate_motion_element(opportunity, job)
            if element:
                motion_elements.append(element)

        # Step 3: Create main Remotion composition
        print(f"   🎬 Creating main composition...")
        main_composition = self._create_main_composition(motion_elements, job)

        # Step 4: Generate package.json and dependencies
        print(f"   📦 Generating project files...")
        project_files = self._generate_project_files(job)

        # Step 5: Create render specifications
        print(f"   ⚙️  Creating render specifications...")
        render_specs = self._create_render_specs(job, motion_elements)

        print(f"✅ Remotion Agent: Generated {len(motion_elements)} motion graphic elements")

        return {
            "motion_elements": [e.to_dict() for e in motion_elements],
            "main_composition": main_composition,
            "project_files": project_files,
            "render_specs": render_specs,
            "total_elements": len(motion_elements)
        }

    async def _analyze_scenes_for_graphics(
        self,
        job: ProductionJob,
        clips: List[SceneClip]
    ) -> List[Dict[str, Any]]:
        """
        Identify moments that would benefit from motion graphics
        Returns list of opportunities with timing and type
        """
        if not self.client:
            return self._get_default_graphic_opportunities(clips)

        try:
            # Build scene summary
            scenes_summary = "\n".join([
                f"Scene {clip.sequence_number} ({clip.duration}s):\n"
                f"  Narration: {clip.narration_text}\n"
                f"  Description: {clip.scene_description}\n"
                f"  Emotion: {clip.emotional_beat}"
                for clip in clips
            ])

            prompt = f"""You are a Vox-style motion graphics designer. Analyze these scenes and identify moments that need animated graphics to help explain concepts.

VIDEO: {job.title}
Topic: {job.topic}
Tone: {job.tone}

SCENES:
{scenes_summary}

For each scene, identify if it needs motion graphics and what type:

MOTION GRAPHIC TYPES:
1. **Animated Text** - Key quotes, statistics, emphasis
2. **Chart/Graph** - Data visualization, comparisons, trends
3. **Diagram** - Process flows, relationships, explanations
4. **Icon Animation** - Visual metaphors, simple concepts
5. **Split Screen** - Before/after, comparisons
6. **Timeline** - Sequential events, historical progression
7. **Map Animation** - Geographic information
8. **Transition** - Scene-to-scene smooth transitions

Vox-style principles:
- Clean, minimal design
- Bold typography
- Smooth spring animations
- Data-driven visualizations
- Colorful but professional
- Helps understanding, not just decoration

Return JSON array of opportunities:
[
  {{
    "scene_number": 1,
    "timing": 2.5,
    "duration": 3.0,
    "type": "animated_text",
    "reason": "Why this helps",
    "content": "What to show",
    "data": {{"text": "KEY POINT", "emphasis": "high"}},
    "style": "bold_fade_in"
  }},
  {{
    "scene_number": 2,
    "timing": 0.5,
    "duration": 4.0,
    "type": "bar_chart",
    "reason": "Visualize comparison",
    "content": "Growth comparison",
    "data": {{"values": [10, 25, 50, 85], "labels": ["2020", "2021", "2022", "2023"]}},
    "style": "animated_bars"
  }}
]

Only suggest graphics that genuinely help understanding. Vox uses graphics purposefully."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            analysis_text = response.content[0].text

            # Extract JSON
            start_idx = analysis_text.find('[')
            end_idx = analysis_text.rfind(']') + 1
            if start_idx != -1 and end_idx > start_idx:
                opportunities = json.loads(analysis_text[start_idx:end_idx])
                return opportunities

        except Exception as e:
            print(f"   ⚠️  Scene analysis failed: {e}")

        return self._get_default_graphic_opportunities(clips)

    async def _generate_motion_element(
        self,
        opportunity: Dict[str, Any],
        job: ProductionJob
    ) -> Optional[MotionGraphicElement]:
        """
        Generate Remotion code for a single motion graphic element
        """
        if not self.client:
            return self._generate_fallback_element(opportunity, job)

        try:
            element_type = opportunity.get('type', 'animated_text')
            content = opportunity.get('content', '')
            data = opportunity.get('data', {})
            style = opportunity.get('style', 'default')

            prompt = f"""Generate Remotion (React) code for this motion graphic element.

ELEMENT:
Type: {element_type}
Content: {content}
Data: {json.dumps(data)}
Style: {style}
Duration: {opportunity.get('duration', 3.0)}s

Generate a complete Remotion component that:
1. Uses Remotion hooks (useCurrentFrame, useVideoConfig, spring, interpolate)
2. Implements smooth animations with spring physics
3. Follows Vox-style design (clean, bold, professional)
4. Is fully typed with TypeScript
5. Exports as a named component

Example structure:
```typescript
import {{ useCurrentFrame, useVideoConfig, spring, interpolate }} from 'remotion';
import React from 'react';

export const MyGraphic: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();

  const progress = spring({{
    frame,
    fps,
    config: {{ damping: 100, stiffness: 200 }}
  }});

  return (
    <div style={{{{ ... }}}}>
      <!-- Your animated graphic here -->
    </div>
  );
}};
```

Generate complete, production-ready Remotion code for: {element_type}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            code_text = response.content[0].text

            # Extract code block
            if '```typescript' in code_text or '```tsx' in code_text:
                start_marker = '```typescript' if '```typescript' in code_text else '```tsx'
                start_idx = code_text.find(start_marker) + len(start_marker)
                end_idx = code_text.find('```', start_idx)
                remotion_code = code_text[start_idx:end_idx].strip()
            else:
                remotion_code = code_text

            scene_number = opportunity.get('scene_number', 1)

            return MotionGraphicElement(
                element_id=f"{job.job_id}_mg_{scene_number}_{element_type}",
                element_type=element_type,
                scene_number=scene_number,
                start_time=opportunity.get('timing', 0),
                duration=opportunity.get('duration', 3.0),
                remotion_code=remotion_code,
                data=data,
                description=opportunity.get('reason', '')
            )

        except Exception as e:
            print(f"   ⚠️  Code generation failed for {opportunity.get('type')}: {e}")

        return self._generate_fallback_element(opportunity, job)

    def _create_main_composition(
        self,
        motion_elements: List[MotionGraphicElement],
        job: ProductionJob
    ) -> str:
        """
        Generate main Remotion composition that combines all elements
        """
        # Generate imports for all element components
        imports = "\n".join([
            f"import {{ {self._get_component_name(elem)} }} from './components/{elem.element_id}';"
            for elem in motion_elements
        ])

        # Generate Sequence components for each element
        sequences = "\n".join([
            f"""      <Sequence
        from={{{int(elem.start_time * 30)}}}
        durationInFrames={{{int(elem.duration * 30)}}}
      >
        <{self._get_component_name(elem)} />
      </Sequence>"""
            for elem in motion_elements
        ])

        composition = f"""import {{ Composition, Sequence }} from 'remotion';
import React from 'react';
{imports}

export const MainComposition: React.FC = () => {{
  return (
    <div style={{{{ width: '100%', height: '100%', backgroundColor: 'transparent' }}}}>
{sequences}
    </div>
  );
}};

// Register composition
export const RemotionRoot: React.FC = () => {{
  return (
    <>
      <Composition
        id="MainComposition"
        component={{MainComposition}}
        durationInFrames={{{int(job.duration_target * 30)}}}
        fps={{30}}
        width={{1920}}
        height={{1080}}
      />
    </>
  );
}};
"""

        return composition

    def _generate_project_files(self, job: ProductionJob) -> Dict[str, str]:
        """
        Generate package.json and other project files
        """
        package_json = {
            "name": f"remotion-{job.job_id}",
            "version": "1.0.0",
            "description": f"Motion graphics for {job.title}",
            "scripts": {
                "start": "remotion preview",
                "build": "remotion render MainComposition out/video.mp4",
                "upgrade": "remotion upgrade"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "remotion": "^4.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "typescript": "^5.0.0"
            }
        }

        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "lib": ["DOM", "ES2022"],
                "jsx": "react-jsx",
                "module": "ESNext",
                "moduleResolution": "node",
                "esModuleInterop": True,
                "skipLibCheck": True,
                "strict": True
            }
        }

        return {
            "package.json": json.dumps(package_json, indent=2),
            "tsconfig.json": json.dumps(tsconfig, indent=2),
            "README.md": f"# Motion Graphics for {job.title}\n\nGenerated by Remotion Agent\n\n## Usage\n\n```bash\nnpm install\nnpm start\n```"
        }

    def _create_render_specs(
        self,
        job: ProductionJob,
        motion_elements: List[MotionGraphicElement]
    ) -> Dict[str, Any]:
        """
        Create rendering specifications for the Remotion project
        """
        return {
            "composition_id": "MainComposition",
            "output_format": "mp4",
            "codec": "h264",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration_in_frames": int(job.duration_target * 30),
            "concurrency": 4,
            "quality": 90,
            "pixel_format": "yuv420p",
            "audio_codec": "aac",
            "audio_bitrate": "320k",
            "transparent_background": True,  # For overlay on main video
            "image_format": "png"  # If rendering as image sequence
        }

    def _get_component_name(self, element: MotionGraphicElement) -> str:
        """Generate React component name from element"""
        return f"Graphic{element.scene_number}{element.element_type.title().replace('_', '')}"

    def _get_default_graphic_opportunities(
        self,
        clips: List[SceneClip]
    ) -> List[Dict[str, Any]]:
        """
        Fallback graphic opportunities when LLM not available
        """
        opportunities = []

        # Add simple text animation for first scene (hook)
        if len(clips) > 0:
            opportunities.append({
                "scene_number": 1,
                "timing": 0.5,
                "duration": 2.0,
                "type": "animated_text",
                "reason": "Emphasize hook",
                "content": "Key opening statement",
                "data": {"text": clips[0].narration_text[:30].upper()},
                "style": "bold_fade_in"
            })

        return opportunities

    def _generate_fallback_element(
        self,
        opportunity: Dict[str, Any],
        job: ProductionJob
    ) -> MotionGraphicElement:
        """
        Generate basic fallback element when code generation fails
        """
        element_type = opportunity.get('type', 'animated_text')
        data = opportunity.get('data', {})

        # Simple animated text template
        fallback_code = f"""import {{ useCurrentFrame, spring }} from 'remotion';
import React from 'react';

export const FallbackGraphic: React.FC = () => {{
  const frame = useCurrentFrame();

  const opacity = spring({{
    frame,
    fps: 30,
    config: {{ damping: 100 }}
  }});

  return (
    <div style={{{{
      opacity,
      fontSize: 60,
      fontWeight: 'bold',
      color: 'white',
      textAlign: 'center',
      padding: 40
    }}}}>
      {data.get('text', 'Animated Text')}
    </div>
  );
}};"""

        return MotionGraphicElement(
            element_id=f"{job.job_id}_mg_fallback",
            element_type=element_type,
            scene_number=opportunity.get('scene_number', 1),
            start_time=opportunity.get('timing', 0),
            duration=opportunity.get('duration', 3.0),
            remotion_code=fallback_code,
            data=data,
            description="[FALLBACK] Basic motion graphic"
        )

    async def export_remotion_project(
        self,
        motion_data: Dict[str, Any],
        output_dir: str
    ):
        """
        Export complete Remotion project to filesystem
        Can be opened and edited in Remotion Studio
        """
        print(f"📁 Remotion Agent: Exporting project to {output_dir}...")

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/src", exist_ok=True)
        os.makedirs(f"{output_dir}/src/components", exist_ok=True)

        # Write project files
        project_files = motion_data.get('project_files', {})
        for filename, content in project_files.items():
            with open(f"{output_dir}/{filename}", 'w') as f:
                f.write(content)

        # Write main composition
        with open(f"{output_dir}/src/Root.tsx", 'w') as f:
            f.write(motion_data.get('main_composition', ''))

        # Write individual components
        for element in motion_data.get('motion_elements', []):
            component_file = f"{output_dir}/src/components/{element['element_id']}.tsx"
            with open(component_file, 'w') as f:
                f.write(element['remotion_code'])

        print(f"✅ Remotion project exported to {output_dir}")
