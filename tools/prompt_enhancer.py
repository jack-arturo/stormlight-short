#!/usr/bin/env python3
"""
Prompt Enhancer - Specialized prompt generation for Midjourney and Veo 3
Tailored for Stormlight Archives animation in Arcane style
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  LLM Generator not available. Some features will be disabled.")

console = Console()

class PromptEnhancer:
    """Enhance and generate prompts for Midjourney and Veo 3"""
    
    # Stormlight-specific visual elements
    STORMLIGHT_ELEMENTS = {
        "environments": [
            "Shattered Plains with deep chasms",
            "highstorm wall approaching",
            "rocky plateaus under stormy skies",
            "crystalline formations",
            "alien moss and lichens",
            "Roshar's reddish sun"
        ],
        "characters": {
            "kaladin": "dark-haired warrior with haunted eyes, windswept appearance",
            "syl": "glowing blue wind spren, ribbon of light, ethereal",
            "bridge_four": "desperate soldiers carrying massive wooden bridge",
            "parshendi": "carapace-armored warriors with gemhearts"
        },
        "atmospheres": [
            "pre-storm tension",
            "electric blue stormlight",
            "dusty battlefield haze",
            "ethereal spren glow",
            "oppressive gray clouds"
        ]
    }
    
    # Arcane style descriptors
    ARCANE_STYLE = {
        "visual": "painterly realism, Fortiche animation style, hand-painted textures",
        "lighting": "dramatic rim lighting, volumetric atmosphere, color contrast",
        "composition": "dynamic angles, depth layers, cinematic framing",
        "color_palettes": {
            "storm": ["slate gray", "electric blue", "deep purple", "silver"],
            "battle": ["rust brown", "blood red", "dust yellow", "steel gray"],
            "mystical": ["ethereal blue", "pearl white", "soft gold", "lavender"],
            "desolate": ["ash gray", "bone white", "faded orange", "charcoal"]
        }
    }
    
    # Camera movements for video generation
    CAMERA_MOVEMENTS = [
        "slow push in",
        "dramatic pull back reveal",
        "sweeping aerial shot",
        "tracking shot following action",
        "orbiting around subject",
        "handheld urgency",
        "smooth dolly forward",
        "crane shot rising up"
    ]
    
    def __init__(self, project_root: Path = None):
        """Initialize the Prompt Enhancer"""
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / "config" / "pipeline_config.yaml"
        self.prompts_dir = self.project_root / "02_prompts"
        self.story_dir = self.project_root / "07_story_development"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize LLM if available
        if LLM_AVAILABLE:
            self.llm = LLMGenerator(project_root=self.project_root)
        else:
            self.llm = None
            console.print("⚠️  Running without LLM enhancement", style="yellow")
    
    def _load_config(self) -> Dict:
        """Load pipeline configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def enhance_midjourney_prompt(self,
                                 base_description: str,
                                 scene_name: str,
                                 frame_type: str = "start",
                                 use_llm: bool = True,
                                 style_reference: bool = True) -> Dict[str, str]:
        """
        Enhance a prompt for Midjourney generation
        
        Args:
            base_description: Basic scene description
            scene_name: Scene identifier
            frame_type: start, end, or reference
            use_llm: Whether to use LLM enhancement
            style_reference: Whether this will use V7 style references
        
        Returns:
            Dictionary with enhanced prompts and workflow notes
        """
        # Get scene configuration
        scene_config = self.config.get("scenes", {}).get(scene_name, {})
        style_descriptors = scene_config.get("style_descriptors", [])
        
        # Build base prompt with Arcane style
        if not style_reference:
            # Full style prompt for initial generation
            style_elements = [
                self.ARCANE_STYLE["visual"],
                "dramatic " + self.ARCANE_STYLE["lighting"].split(',')[0]
            ]
            
            # Add scene-specific color palette
            if "storm" in scene_name or "storm" in base_description.lower():
                palette = self.ARCANE_STYLE["color_palettes"]["storm"]
            elif "battle" in scene_name or "bridge" in scene_name:
                palette = self.ARCANE_STYLE["color_palettes"]["battle"]
            elif "spren" in base_description.lower():
                palette = self.ARCANE_STYLE["color_palettes"]["mystical"]
            else:
                palette = self.ARCANE_STYLE["color_palettes"]["desolate"]
            
            style_elements.append(f"color palette: {', '.join(palette[:3])}")
            full_style = ", ".join(style_elements)
            
            base_prompt = f"{base_description}, {full_style}"
        else:
            # Simple content prompt for style reference workflow
            base_prompt = base_description
        
        # Use LLM enhancement if available
        if use_llm and self.llm:
            enhanced = self._enhance_with_llm(
                base_prompt,
                scene_name,
                frame_type,
                style_descriptors
            )
        else:
            enhanced = self._enhance_manually(
                base_prompt,
                scene_name,
                frame_type,
                style_descriptors
            )
        
        # Add Midjourney parameters
        if style_reference:
            # V7 Style References workflow
            enhanced["workflow"] = "V7_STYLE_REFERENCES"
            enhanced["parameters"] = "--sw 300 --ar 16:9 --q 2"
            enhanced["note"] = "Upload previous clip + start frame as Style References"
        else:
            # Standard generation
            enhanced["workflow"] = "STANDARD"
            enhanced["parameters"] = "--style raw --ar 16:9 --q 2 --no text"
        
        # Combine prompt with parameters
        for key in ["simple", "detailed", "artistic"]:
            if key in enhanced:
                enhanced[key] = f"{enhanced[key]} {enhanced['parameters']}"
        
        return enhanced
    
    def enhance_veo_prompt(self,
                         base_description: str,
                         scene_name: str,
                         duration: int = 8,
                         camera_movement: str = None,
                         mood: str = None,
                         use_llm: bool = True) -> Dict[str, Any]:
        """
        Enhance a prompt for Veo 3 video generation
        
        Args:
            base_description: Basic scene description
            scene_name: Scene identifier
            duration: Video duration in seconds
            camera_movement: Specific camera movement
            mood: Desired mood/atmosphere
            use_llm: Whether to use LLM enhancement
        
        Returns:
            Dictionary with enhanced prompt and metadata
        """
        # Get scene configuration
        scene_config = self.config.get("scenes", {}).get(scene_name, {})
        
        # Select camera movement if not specified
        if not camera_movement:
            if "action" in scene_config.get("style_descriptors", []):
                camera_movement = "tracking shot following action"
            elif "massive" in scene_config.get("style_descriptors", []):
                camera_movement = "dramatic pull back reveal"
            else:
                camera_movement = "slow push in"
        
        # Build video prompt with temporal elements
        temporal_elements = [
            f"{duration} second clip",
            camera_movement,
            "smooth motion",
            "cinematic pacing"
        ]
        
        # Add mood if specified
        if mood:
            temporal_elements.append(f"{mood} atmosphere")
        
        # Use LLM enhancement if available
        if use_llm and self.llm:
            enhanced = self._enhance_video_with_llm(
                base_description,
                scene_name,
                temporal_elements,
                mood
            )
        else:
            # Manual enhancement
            video_prompt = f"{base_description}, {', '.join(temporal_elements)}"
            enhanced = {
                "prompt": video_prompt,
                "simple": base_description,
                "detailed": video_prompt
            }
        
        # Add metadata
        enhanced["metadata"] = {
            "scene": scene_name,
            "duration": duration,
            "camera_movement": camera_movement,
            "mood": mood,
            "timestamp": datetime.now().isoformat()
        }
        
        return enhanced
    
    def _enhance_with_llm(self,
                         base_prompt: str,
                         scene_name: str,
                         frame_type: str,
                         style_descriptors: List[str]) -> Dict[str, str]:
        """Use LLM to enhance Midjourney prompt"""
        
        system_prompt = f"""You are a Midjourney prompt specialist for Stormlight Archives animation.
        Create prompts in Arcane/Fortiche animation style.
        
        Scene: {scene_name}
        Frame Type: {frame_type}
        Style Keywords: {', '.join(style_descriptors)}
        
        Guidelines:
        - Use clear, descriptive language
        - Avoid abstract concepts
        - Include specific visual details
        - Maintain Arcane animation style
        - No text or writing in scenes
        - Focus on composition and mood"""
        
        # Generate variations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Enhancing {frame_type} frame prompt...", total=1)
            
            response = self.llm.generate(
                prompt=f"Create 3 prompt variations for: {base_prompt}",
                system_prompt=system_prompt,
                max_tokens=400,
                temperature=0.7
            )
            
            progress.update(task, completed=1)
        
        # Parse response into variations
        lines = response["content"].split('\n')
        prompts = {
            "simple": base_prompt,
            "detailed": "",
            "artistic": ""
        }
        
        variation_count = 0
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                clean_line = line.lstrip('0123456789.-) ').strip()
                if clean_line:
                    if variation_count == 0:
                        prompts["simple"] = clean_line
                    elif variation_count == 1:
                        prompts["detailed"] = clean_line
                    elif variation_count == 2:
                        prompts["artistic"] = clean_line
                    variation_count += 1
        
        # Ensure we have all variations
        if not prompts["detailed"]:
            prompts["detailed"] = prompts["simple"] + ", detailed environment"
        if not prompts["artistic"]:
            prompts["artistic"] = prompts["simple"] + ", painterly style"
        
        return prompts
    
    def _enhance_manually(self,
                         base_prompt: str,
                         scene_name: str,
                         frame_type: str,
                         style_descriptors: List[str]) -> Dict[str, str]:
        """Manual enhancement without LLM"""
        
        # Add style descriptors
        enhanced = base_prompt
        if style_descriptors:
            enhanced += f", {', '.join(style_descriptors[:2])}"
        
        # Add frame-specific elements
        if frame_type == "start":
            enhanced += ", establishing shot"
        elif frame_type == "end":
            enhanced += ", concluding moment"
        
        return {
            "simple": base_prompt,
            "detailed": enhanced,
            "artistic": enhanced + ", artistic composition"
        }
    
    def _enhance_video_with_llm(self,
                               base_description: str,
                               scene_name: str,
                               temporal_elements: List[str],
                               mood: str) -> Dict[str, str]:
        """Use LLM to enhance video prompt"""
        
        system_prompt = f"""You are a video prompt specialist for AI video generation.
        Create prompts for smooth, cinematic 8-second clips.
        
        Scene: {scene_name}
        Mood: {mood or 'dramatic'}
        
        Guidelines:
        - Describe motion and progression
        - Include camera movement
        - Specify lighting changes
        - Maintain visual continuity
        - Focus on smooth, realistic motion"""
        
        response = self.llm.generate(
            prompt=f"Enhance this video prompt: {base_description}\nElements: {', '.join(temporal_elements)}",
            system_prompt=system_prompt,
            max_tokens=200,
            temperature=0.6
        )
        
        enhanced_prompt = response["content"].strip()
        
        return {
            "prompt": enhanced_prompt,
            "simple": base_description,
            "detailed": enhanced_prompt,
            "cost": response["cost"]
        }
    
    def generate_scene_variations(self,
                                 scene_name: str,
                                 num_variations: int = 5,
                                 variation_type: str = "mood") -> List[Dict[str, str]]:
        """
        Generate multiple variations for a scene
        
        Args:
            scene_name: Scene identifier
            num_variations: Number of variations
            variation_type: mood, camera, time, weather
        
        Returns:
            List of variation dictionaries
        """
        # Get base scene configuration
        scene_config = self.config.get("scenes", {}).get(scene_name, {})
        base_description = scene_config.get("description", "")
        default_prompts = scene_config.get("default_prompts", [])
        
        if not base_description and default_prompts:
            base_description = default_prompts[0]
        
        variations = []
        
        if self.llm:
            # Use LLM to generate variations
            variation_prompts = self.llm.generate_variations(
                base_description,
                num_variations=num_variations,
                variation_type=variation_type
            )
            
            for i, prompt in enumerate(variation_prompts):
                variations.append({
                    "variation": i + 1,
                    "type": variation_type,
                    "prompt": prompt,
                    "midjourney": self.enhance_midjourney_prompt(
                        prompt, scene_name, use_llm=False
                    ),
                    "veo": self.enhance_veo_prompt(
                        prompt, scene_name, use_llm=False
                    )
                })
        else:
            # Manual variations
            moods = ["heroic", "desperate", "mystical", "ominous", "triumphant"]
            cameras = ["aerial wide", "close up intense", "tracking action", "slow reveal", "orbiting"]
            
            for i in range(min(num_variations, 5)):
                if variation_type == "mood":
                    modifier = moods[i % len(moods)]
                else:
                    modifier = cameras[i % len(cameras)]
                
                prompt = f"{base_description}, {modifier}"
                variations.append({
                    "variation": i + 1,
                    "type": variation_type,
                    "prompt": prompt,
                    "midjourney": self.enhance_midjourney_prompt(
                        prompt, scene_name, use_llm=False
                    ),
                    "veo": self.enhance_veo_prompt(
                        prompt, scene_name, use_llm=False
                    )
                })
        
        return variations
    
    def analyze_prompt_continuity(self,
                                 prompts: List[str],
                                 suggest_fixes: bool = True) -> Dict[str, Any]:
        """
        Analyze continuity between a sequence of prompts
        
        Args:
            prompts: List of prompts in sequence
            suggest_fixes: Whether to suggest improvements
        
        Returns:
            Continuity analysis with suggestions
        """
        if not self.llm:
            return {
                "analysis": "LLM not available for continuity analysis",
                "issues": [],
                "suggestions": []
            }
        
        issues = []
        suggestions = []
        
        # Analyze each transition
        for i in range(len(prompts) - 1):
            result = self.llm.analyze_continuity(
                prompts[i],
                prompts[i + 1],
                suggest_transition=suggest_fixes
            )
            
            # Parse analysis for issues
            if "lighting" in result["analysis"].lower():
                issues.append(f"Lighting inconsistency between scenes {i+1} and {i+2}")
            if "color" in result["analysis"].lower():
                issues.append(f"Color palette shift between scenes {i+1} and {i+2}")
            if "style" in result["analysis"].lower():
                issues.append(f"Style inconsistency between scenes {i+1} and {i+2}")
            
            # Extract suggestions
            if suggest_fixes and "suggest" in result["analysis"].lower():
                suggestions.append({
                    "transition": f"Scene {i+1} to {i+2}",
                    "suggestion": result["analysis"].split("suggest")[-1].strip()
                })
        
        return {
            "analysis": "Continuity check complete",
            "issues": issues,
            "suggestions": suggestions,
            "prompt_count": len(prompts)
        }
    
    def save_enhanced_prompts(self,
                             scene_name: str,
                             prompts: Dict[str, Any],
                             filename: str = None):
        """Save enhanced prompts to file"""
        filename = filename or f"{scene_name}_enhanced_prompts.json"
        filepath = self.prompts_dir / "enhanced" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        console.print(f"💾 Saved enhanced prompts: {filepath}")
    
    def display_enhancement_results(self,
                                   scene_name: str,
                                   results: Dict[str, Any]):
        """Display enhancement results in a formatted table"""
        table = Table(title=f"Enhanced Prompts for {scene_name}")
        table.add_column("Type", style="cyan")
        table.add_column("Prompt", style="white", overflow="fold")
        
        for key, value in results.items():
            if key not in ["metadata", "workflow", "parameters", "note"]:
                if isinstance(value, str):
                    # Truncate long prompts for display
                    display_value = value[:100] + "..." if len(value) > 100 else value
                    table.add_row(key.title(), display_value)
        
        console.print(table)
        
        # Show metadata if available
        if "metadata" in results:
            console.print("\n📊 Metadata:", style="bold")
            for key, value in results["metadata"].items():
                console.print(f"  {key}: {value}")
        
        # Show cost if LLM was used
        if self.llm:
            stats = self.llm.get_usage_stats()
            console.print(f"\n💰 Generation cost: ${stats['total_cost']:.4f}")


def main():
    """Test the prompt enhancer"""
    enhancer = PromptEnhancer()
    
    console.print(Panel.fit("🎨 Prompt Enhancer Test", style="bold cyan"))
    
    # Test Midjourney enhancement
    console.print("\n📸 Midjourney Prompt Enhancement:")
    midjourney_result = enhancer.enhance_midjourney_prompt(
        "Kaladin standing on cliff edge",
        "kaladin_intro",
        frame_type="start",
        use_llm=True
    )
    enhancer.display_enhancement_results("kaladin_intro", midjourney_result)
    
    # Test Veo enhancement
    console.print("\n🎬 Veo 3 Video Prompt Enhancement:")
    veo_result = enhancer.enhance_veo_prompt(
        "Bridge crew running across chasm",
        "bridge_run",
        camera_movement="tracking shot",
        mood="desperate",
        use_llm=True
    )
    enhancer.display_enhancement_results("bridge_run", veo_result)
    
    # Test variations
    console.print("\n🔄 Scene Variations:")
    variations = enhancer.generate_scene_variations(
        "kaladin_intro",
        num_variations=3,
        variation_type="mood"
    )
    for var in variations:
        console.print(f"  Variation {var['variation']}: {var['prompt'][:80]}...")


if __name__ == "__main__":
    main()