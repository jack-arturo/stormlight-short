#!/usr/bin/env python3
"""
Styleframe Manager - Organize and manage Midjourney styleframes for video generation
Handles start frames, end frames, and reference images for each scene.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import time
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from prompt_enhancer import PromptEnhancer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  LLM enhancement not available. Install with: pip install openai")

console = Console()

class StyleframeManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.styleframes_dir = self.project_root / "01_styleframes_midjourney"
        
        # Organized subdirectories
        self.scenes_dir = self.styleframes_dir / "scenes"
        self.start_frames_dir = self.styleframes_dir / "start_frames"
        self.end_frames_dir = self.styleframes_dir / "end_frames"
        self.reference_dir = self.styleframes_dir / "reference"
        
        # Metadata file
        self.metadata_file = self.styleframes_dir / "styleframes_metadata.json"
        
        # Ensure directories exist
        for dir_path in [self.scenes_dir, self.start_frames_dir, self.end_frames_dir, self.reference_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.console = Console()
        
        # Project-agnostic story development detection
        self.story_dev_dir = self.project_root / "07_story_development"
        
        # Initialize prompt enhancer if available
        if LLM_AVAILABLE:
            self.prompt_enhancer = PromptEnhancer(project_root=self.project_root)
        else:
            self.prompt_enhancer = None
    
    def organize_styleframe(self, 
                           image_path: Path, 
                           scene_name: str,
                           frame_type: str = "reference",
                           description: str = "",
                           midjourney_prompt: str = "") -> Dict[str, str]:
        """
        Organize a styleframe into the proper directory structure
        
        Args:
            image_path: Path to the source image
            scene_name: Scene identifier (e.g., 'kaladin_intro')
            frame_type: 'start', 'end', or 'reference'
            description: Human-readable description
            midjourney_prompt: Original Midjourney prompt used
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if frame_type not in ['start', 'end', 'reference']:
            raise ValueError("frame_type must be 'start', 'end', or 'reference'")
        
        # Determine target directory
        if frame_type == "start":
            target_dir = self.start_frames_dir
        elif frame_type == "end":
            target_dir = self.end_frames_dir
        else:
            target_dir = self.reference_dir
        
        # Create scene-specific subdirectory
        scene_dir = target_dir / scene_name
        scene_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp (always use .jpg for optimization)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{scene_name}_{frame_type}_{timestamp}.jpg"
        target_path = scene_dir / new_filename
        
        # Optimize and copy the file
        console.print(f"🔄 Processing {image_path.name}...")
        optimized = self._optimize_image(image_path, target_path)
        
        # Update metadata
        metadata = self._load_metadata()
        entry = {
            "scene_name": scene_name,
            "frame_type": frame_type,
            "filename": new_filename,
            "path": str(target_path.relative_to(self.project_root)),
            "description": description,
            "midjourney_prompt": midjourney_prompt,
            "timestamp": timestamp,
            "original_path": str(image_path)
        }
        
        if scene_name not in metadata:
            metadata[scene_name] = {}
        if frame_type not in metadata[scene_name]:
            metadata[scene_name][frame_type] = []
        
        metadata[scene_name][frame_type].append(entry)
        self._save_metadata(metadata)
        
        console.print(f"✅ Organized {frame_type} frame for {scene_name}: {new_filename}")
        return entry
    
    def get_scene_styleframes(self, scene_name: str) -> Dict[str, List[Dict]]:
        """Get all styleframes for a specific scene"""
        metadata = self._load_metadata()
        return metadata.get(scene_name, {})
    
    def get_best_reference_image(self, scene_name: str, frame_type: str = "start") -> Optional[Path]:
        """
        Get the best reference image for a scene
        Prioritizes start frames, then reference images, then end frames
        """
        metadata = self._load_metadata()
        scene_data = metadata.get(scene_name, {})
        
        # Priority order: start -> reference -> end
        priority_order = ["start", "reference", "end"] if frame_type == "start" else ["end", "reference", "start"]
        
        for ftype in priority_order:
            if ftype in scene_data and scene_data[ftype]:
                # Get the most recent one
                latest = max(scene_data[ftype], key=lambda x: x["timestamp"])
                return self.project_root / latest["path"]
        
        return None
    
    def list_scenes_with_styleframes(self) -> Dict[str, Dict]:
        """List all scenes that have styleframes"""
        metadata = self._load_metadata()
        return metadata
    
    def generate_midjourney_prompts(self, scene_name: str, base_description: str, 
                                   start_frame_path: str = None, use_llm: bool = False,
                                   num_variations: int = 3) -> Dict[str, str]:
        """
        Generate clean Midjourney prompts optimized for --style raw
        
        Args:
            scene_name: Scene identifier
            base_description: Base scene description
            start_frame_path: Path to start frame for style reference (optional)
            use_llm: Whether to use LLM enhancement
            num_variations: Number of variations to generate (when using LLM)
        """
        # Use LLM enhancement if requested and available
        if use_llm and self.prompt_enhancer:
            console.print("🤖 Using LLM enhancement for prompts...", style="cyan")
            
            # Generate enhanced prompts for start frame
            start_enhanced = self.prompt_enhancer.enhance_midjourney_prompt(
                base_description,
                scene_name,
                frame_type="start",
                use_llm=True,
                style_reference=False
            )
            
            # Generate enhanced prompts for end frame (with style references)
            end_enhanced = self.prompt_enhancer.enhance_midjourney_prompt(
                base_description,
                scene_name,
                frame_type="end",
                use_llm=True,
                style_reference=True if start_frame_path else False
            )
            
            # Generate variations if requested
            if num_variations > 1:
                variations = self.prompt_enhancer.generate_scene_variations(
                    scene_name,
                    num_variations=num_variations,
                    variation_type="mood"
                )
                
                # Add variations to the result
                prompts = {
                    "start_frame": start_enhanced.get("detailed", base_description),
                    "end_frame_simple": end_enhanced.get("simple", base_description),
                    "end_frame_detailed": end_enhanced.get("detailed", base_description),
                    "workflow_note": end_enhanced.get("note", "Use V7 Style References"),
                    "variations": []
                }
                
                for var in variations:
                    prompts["variations"].append(var["midjourney"]["detailed"])
                
                # Display cost if available
                if self.prompt_enhancer.llm:
                    stats = self.prompt_enhancer.llm.get_usage_stats()
                    console.print(f"💰 LLM cost: ${stats['total_cost']:.4f}", style="dim")
            else:
                prompts = {
                    "start_frame": start_enhanced.get("detailed", base_description),
                    "end_frame_simple": end_enhanced.get("simple", base_description),
                    "end_frame_detailed": end_enhanced.get("detailed", base_description),
                    "workflow_note": end_enhanced.get("note", "Use V7 Style References")
                }
            
            return prompts
        else:
            # Fall back to manual generation
            if use_llm and not self.prompt_enhancer:
                console.print("⚠️  LLM enhancement requested but not available, using manual generation", style="yellow")
            return self._generate_raw_prompts(scene_name, base_description, start_frame_path)
    

    
    def _generate_raw_prompts(self, scene_name: str, base_description: str, start_frame_path: str = None) -> Dict[str, str]:
        """Generate simple, content-focused prompts optimized for V7 Style References"""
        
        # Scene-specific content variations (no style words to avoid conflicts)
        scene_variations = {
            "title_sequence": {
                "start": "sweeping aerial view of alien landscape with stormy skies",
                "end": "same landscape composition with dramatic storm clouds"
            },
            "kaladin_intro": {
                "start": "close-up portrait of dark-haired young man with slave brands",
                "end": "wider shot showing the same character in full context"
            },
            "adolin_intro": {
                "start": "portrait of handsome young man in military uniform",
                "end": "same character demonstrating sword technique"
            },
            "dalinar_intro": {
                "start": "older man in ornate armor studying battle maps",
                "end": "same character looking up with commanding presence"
            },
            "shattered_plains": {
                "start": "high aerial view of plateau tops and chasm system",
                "end": "deep inside chasm looking up at canyon walls with mist"
            },
            "shattered_plains_reveal": {
                "start": "high aerial view of plateau tops and chasm system",
                "end": "deep inside chasm looking up at canyon walls with mist"
            }
        }
        
        # Get scene-specific variations or use defaults
        variations = scene_variations.get(scene_name, {
            "start": "establishing shot",
            "end": "closer detailed view"
        })
        
        # Simple, content-focused prompts (V7 Style References best practice)
        prompts = {
            "start_frame": f"{base_description} {variations['start']} --no text --ar 16:9 --q 2"
        }
        
        # End frame workflow depends on whether we have style references
        if start_frame_path:
            # V7 Style References workflow - simple content prompts
            prompts["end_frame_simple"] = f"{variations['end']} --sw 300 --ar 16:9 --q 2"
            prompts["end_frame_detailed"] = f"{base_description} {variations['end']} --sw 300 --ar 16:9 --q 2"
            prompts["workflow_note"] = "V7 STYLE REFERENCES WORKFLOW: 1) Generate start frame with simple content prompt, 2) Click start frame to expand, 3) Add Style References (upload previous clip + start frame), 4) Use simple descriptive prompts (avoid style words), 5) Adjust --sw 200-400 for style strength, 6) Generate variations. Let references handle the style!"
        else:
            prompts["end_frame"] = f"{base_description} {variations['end']} --no text --ar 16:9 --q 2"
            prompts["workflow_note"] = "V7 WORKFLOW: 1) Generate start frame first with simple content description, 2) Then use Style References workflow for matching end frame. Avoid style words that conflict with references."
        
        return prompts
    
    def create_scene_report(self, scene_name: str = None) -> None:
        """Create a visual report of styleframes"""
        metadata = self._load_metadata()
        
        if scene_name:
            scenes_to_show = {scene_name: metadata.get(scene_name, {})}
        else:
            scenes_to_show = metadata
        
        for scene, data in scenes_to_show.items():
            table = Table(title=f"Styleframes for {scene}")
            table.add_column("Type", style="cyan")
            table.add_column("Count", style="green")
            table.add_column("Latest", style="yellow")
            table.add_column("Description", style="dim")
            
            for frame_type in ["start", "reference", "end"]:
                frames = data.get(frame_type, [])
                if frames:
                    latest = max(frames, key=lambda x: x["timestamp"])
                    table.add_row(
                        frame_type.title(),
                        str(len(frames)),
                        latest["timestamp"],
                        latest["description"][:50] + "..." if len(latest["description"]) > 50 else latest["description"]
                    )
                else:
                    table.add_row(frame_type.title(), "0", "-", "No frames")
            
            console.print(table)
            console.print()
    
    def _load_metadata(self) -> Dict:
        """Load styleframes metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self, metadata: Dict) -> None:
        """Save styleframes metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _save_prompts_to_story_markdown(self, scene_name: str, prompts: Dict) -> None:
        """Save enhanced prompts to story development markdown files"""
        if not self.story_dev_dir.exists():
            return
        
        # Create an enhanced prompts file in story development
        enhanced_file = self.story_dev_dir / f"enhanced_prompts_{scene_name}.md"
        
        with open(enhanced_file, 'w') as f:
            f.write(f"# Enhanced Prompts for {scene_name}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if "variations" in prompts and prompts["variations"]:
                f.write("🤖 **AI-Enhanced with GPT-4-mini**\n\n")
            
            f.write("## Midjourney Prompts\n\n")
            
            # Start frame
            if "start_frame" in prompts:
                f.write("### Start Frame\n")
                f.write("```\n")
                f.write(prompts['start_frame'])
                f.write("\n```\n\n")
            
            # Variations
            if "variations" in prompts and prompts["variations"]:
                f.write("### Variations\n\n")
                for i, variation in enumerate(prompts["variations"], 1):
                    f.write(f"**Variation {i}:**\n")
                    f.write("```\n")
                    f.write(variation)
                    f.write("\n```\n\n")
            
            # End frame options
            f.write("### End Frame (with Style References)\n\n")
            if "end_frame_simple" in prompts:
                f.write("**Simple (Recommended):**\n")
                f.write("```\n")
                f.write(prompts['end_frame_simple'])
                f.write("\n```\n\n")
            
            if "end_frame_detailed" in prompts:
                f.write("**Detailed:**\n")
                f.write("```\n")
                f.write(prompts['end_frame_detailed'])
                f.write("\n```\n\n")
            
            # Add workflow notes
            f.write("## Workflow Notes\n\n")
            f.write("1. Generate start frame with the simple prompt\n")
            f.write("2. Use V7 Style References for end frame\n")
            f.write("3. Upload start frame + previous clip as references\n")
            f.write("4. Use `--sw 200-400` for style strength\n")
        
        console.print(f"📝 Saved to story development: {enhanced_file}")
    
    def _save_prompts_to_files(self, scene_name: str, prompts: Dict) -> None:
        """Save prompts to files for easy copy-pasting"""
        prompts_dir = self.project_root / "02_prompts" / "midjourney"
        prompts_dir.mkdir(exist_ok=True)
        
        # Use consistent filename without timestamp
        filename = f"{scene_name}_prompts.txt"
        filepath = prompts_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"Midjourney Prompts for {scene_name}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Add AI enhancement note if applicable
            if "variations" in prompts and prompts["variations"]:
                f.write("🤖 AI-Enhanced with Variations\n")
            f.write("\n")
            
            # Always show start frame first and clearly
            if "start_frame" in prompts:
                f.write("🎬 STEP 1 - Generate Start Frame (Simple Content Prompt):\n")
                f.write(f"{prompts['start_frame']}\n\n")
            
            # Show variations if present
            if "variations" in prompts and prompts["variations"]:
                f.write("🔄 Alternative Variations (Different Moods/Styles):\n")
                for i, variation in enumerate(prompts["variations"], 1):
                    f.write(f"\nVariation {i}:\n")
                    f.write(f"{variation}\n")
                f.write("\n")
            
            # Show workflow note
            if "workflow_note" in prompts:
                f.write("📋 V7 Style References Workflow:\n")
                f.write(f"{prompts['workflow_note']}\n\n")
            
            # Show end frame prompts for Style References
            f.write("🎨 STEP 2 - End Frame with Style References:\n")
            for frame_type, prompt in prompts.items():
                if frame_type not in ["start_frame", "workflow_note", "variations"]:
                    if "simple" in frame_type:
                        f.write(f"Simple Content Prompt (Recommended):\n")
                    elif "detailed" in frame_type:
                        f.write(f"Detailed Content Prompt (Alternative):\n")
                    else:
                        f.write(f"{frame_type.replace('_', ' ').title()}:\n")
                    f.write(f"{prompt}\n\n")
            
            f.write("💡 Remember: Upload your start frame + any previous clip as Style References!\n")
            f.write("💡 Use --sw 200-400 to control style influence strength.\n")
        
        console.print(f"💾 Saved: {filepath}")

    def interactive_workflow(self, scene_name: str, base_description: str, use_llm: bool = None) -> None:
        """Interactive workflow that walks user through the entire process"""
        console.print(Panel.fit(
            f"🎬 Interactive Styleframe Workflow for [bold cyan]{scene_name}[/bold cyan]",
            style="bold blue"
        ))
        
        # Ask about LLM enhancement if not specified and available
        if use_llm is None and self.prompt_enhancer:
            console.print("\n[bold cyan]🤖 AI Enhancement Available[/bold cyan]")
            console.print("Would you like to use AI to enhance your prompts?")
            console.print("• [bold green]Yes:[/bold green] Generate cinematic prompts with variations")
            console.print("• [bold yellow]No:[/bold yellow] Use standard prompt generation")
            use_llm = Confirm.ask("Use AI enhancement?", default=True)
        elif use_llm is None:
            use_llm = False
        
        # Step 1: Introduce V7 Style References Workflow
        console.print("\n[bold cyan]🎨 Midjourney V7 Style References Workflow[/bold cyan]")
        console.print("This workflow uses Style References for consistent visual style across clips.")
        console.print("\n[bold yellow]✅ V7 Best Practices:[/bold yellow]")
        console.print("• [bold green]Simple Prompts:[/bold green] Focus on content, not style words")
        console.print("• [bold green]Style References:[/bold green] Upload images to control visual style")
        console.print("• [bold green]Style Weight:[/bold green] Use --sw 200-400 to control influence")
        console.print("• [bold red]Avoid:[/bold red] 'copy this style', 'the look of this image but...'")
        console.print("• [bold green]Good:[/bold green] 'detailed portrait of Kaladin', 'chasm depths with mist'")
        
        # Generate prompts with optional LLM enhancement
        console.print("\n[bold yellow]Step 1: Generate simple start frame prompt...[/bold yellow]")
        if use_llm:
            console.print("🤖 Using AI to enhance prompts...")
            num_variations = 3
            if Confirm.ask("Would you like multiple variations?", default=True):
                num_variations = int(Prompt.ask("How many variations?", default="3"))
        else:
            num_variations = 1
        
        prompts = self.generate_midjourney_prompts(
            scene_name, 
            base_description,
            use_llm=use_llm,
            num_variations=num_variations
        )
        
        # Display start frame prompt (plain text for easy copying)
        console.print("\n[bold green]🎨 Start Frame Prompt (Simple & Content-Focused):[/bold green]")
        console.print("=" * 80)
        console.print(prompts["start_frame"])
        console.print("=" * 80)
        
        # Display variations if generated
        if "variations" in prompts and prompts["variations"]:
            console.print("\n[bold magenta]🔄 Alternative Variations:[/bold magenta]")
            for i, variation in enumerate(prompts["variations"], 1):
                console.print(f"\n[bold cyan]Variation {i}:[/bold cyan]")
                console.print(variation)
        
        # Wait for user to generate start frame
        console.print("\n[bold yellow]Step 2: Generate your start frame[/bold yellow]")
        console.print("1. Copy the simple prompt above")
        console.print("2. Paste it into Midjourney")
        console.print("3. Generate and save your favorite result")
        console.print("4. [bold cyan]Note:[/bold cyan] This will be your style reference for the end frame")
        
        if not Confirm.ask("\nHave you generated and saved your start frame?"):
            console.print("❌ Come back when you have your start frame ready!")
            return
        
        # Step 3: Organize start frame
        console.print("\n[bold yellow]Step 3: Organize your start frame[/bold yellow]")
        console.print("💡 Save your image to tmp/tmp.png (will auto-optimize to JPG)")
        
        # Check for both PNG and JPG in tmp, default to PNG
        png_path = Path("tmp/tmp.png")
        jpg_path = Path("tmp/tmp.jpg")
        
        if png_path.exists():
            start_frame_path = png_path
        elif jpg_path.exists():
            start_frame_path = jpg_path
        else:
            start_frame_path = Path(Prompt.ask("Enter the path to your start frame image"))
        
        if not start_frame_path.exists():
            console.print(f"❌ File not found: {start_frame_path}")
            return
        
        # Organize the start frame
        try:
            entry = self.organize_styleframe(
                start_frame_path,
                scene_name,
                "start",
                f"{scene_name} start frame - interactive workflow",
                prompts["start_frame"]
            )
            console.print(f"✅ Start frame organized: {entry['path']}")
        except Exception as e:
            console.print(f"❌ Error organizing start frame: {e}")
            return
        
        # Step 4: V7 Style References End Frame Workflow
        console.print("\n[bold yellow]Step 4: Generate matching end frame with Style References[/bold yellow]")
        console.print("Now we'll use V7 Style References to create a perfectly matching end frame.")
        
        # Generate prompts with start frame reference
        ref_prompts = self.generate_midjourney_prompts(scene_name, base_description, str(entry['path']))
        
        # Check for previous clip's end frame for consistency
        prev_clip_ref = self._get_previous_clip_reference(scene_name)
        
        console.print("\n[bold cyan]🎨 V7 Style References Step-by-Step:[/bold cyan]")
        console.print("1. [bold yellow]Click Your Start Frame:[/bold yellow] Click the start frame you just generated to expand it")
        console.print("2. [bold yellow]Find 'Style References':[/bold yellow] Look for the Style References section in the expanded view")
        console.print("3. [bold yellow]Upload References:[/bold yellow]")
        
        if prev_clip_ref:
            console.print(f"   📁 [bold green]Previous Clip:[/bold green] Upload {prev_clip_ref} for visual continuity")
        
        console.print(f"   📁 [bold green]Start Frame:[/bold green] Upload your start frame: {entry['path']}")
        console.print("4. [bold yellow]Simple Content Prompt:[/bold yellow] Use the clean prompt below (no style words!)")
        console.print("5. [bold yellow]Set Style Weight:[/bold yellow] Add --sw 200-400 (higher = stronger style influence)")
        console.print("6. [bold yellow]Generate Variations:[/bold yellow] Create multiple options and save the best")
        
        # Show the simple prompts
        if "end_frame_simple" in ref_prompts:
            console.print("\n[bold green]🎨 Simple Content Prompt (Recommended):[/bold green]")
            console.print("=" * 60)
            console.print(ref_prompts["end_frame_simple"])
            console.print("=" * 60)
        
        if "end_frame_detailed" in ref_prompts:
            console.print("\n[bold green]🎨 Alternative Detailed Prompt:[/bold green]")
            console.print("=" * 60)
            console.print(ref_prompts["end_frame_detailed"])
            console.print("=" * 60)
        
        console.print("\n[bold yellow]💡 V7 Style References Best Practices:[/bold yellow]")
        console.print("• [bold green]✅ GOOD:[/bold green] 'detailed portrait of Kaladin', 'chasm depths with mist'")
        console.print("• [bold red]❌ BAD:[/bold red] 'the look of this image but...', 'copy this style and...'")
        console.print("• [bold cyan]CONTENT FOCUS:[/bold cyan] Describe what you want to see, not how to modify references")
        console.print("• [bold cyan]STYLE WEIGHT:[/bold cyan] --sw 0-1000 (default 100, try 200-400 for stronger influence)")
        console.print("• [bold cyan]MULTIPLE REFS:[/bold cyan] Upload 2-3 reference images for best consistency")
        console.print("• [bold cyan]NO STYLE CONFLICTS:[/bold cyan] Avoid style words that fight your uploaded references")
        console.print("• [bold cyan]WEB UI ONLY:[/bold cyan] Upload images directly, no --sref URLs needed")
        
        # Wait for end frame generation
        if not Confirm.ask("\nHave you generated your end frame?"):
            console.print("💾 Prompts saved to file for later use")
            self._save_prompts_to_files(scene_name, ref_prompts)
            return
        
        # Step 5: Organize end frame
        console.print("\n[bold yellow]Step 5: Organize your end frame[/bold yellow]")
        console.print("💡 Save your end frame to tmp/tmp.png (will auto-optimize)")
        
        # Check for both PNG and JPG in tmp for end frame, default to PNG
        png_path = Path("tmp/tmp.png")
        jpg_path = Path("tmp/tmp.jpg")
        
        if png_path.exists():
            end_frame_path = png_path
        elif jpg_path.exists():
            end_frame_path = jpg_path
        else:
            end_frame_path = Path(Prompt.ask("Enter the path to your end frame image"))
        
        if not end_frame_path.exists():
            console.print(f"❌ File not found: {end_frame_path}")
            return
        
        # Organize the end frame
        try:
            end_entry = self.organize_styleframe(
                end_frame_path,
                scene_name,
                "end",
                f"{scene_name} end frame - interactive workflow",
                ref_prompts.get("end_frame_variation", ref_prompts.get("end_frame_full", ""))
            )
            console.print(f"✅ End frame organized: {end_entry['path']}")
        except Exception as e:
            console.print(f"❌ Error organizing end frame: {e}")
            return
        
        # Step 6: Success summary
        console.print(Panel.fit(
            f"🎉 [bold green]Success![/bold green]\n\n"
            f"✅ Start frame: {entry['path']}\n"
            f"✅ End frame: {end_entry['path']}\n\n"
            f"Your {scene_name} styleframes are ready for Veo3 video generation!",
            style="bold green"
        ))
        
        # Save prompts for reference
        self._save_prompts_to_files(scene_name, ref_prompts)
        console.print(f"💾 All prompts saved for future reference")
        
        # Also save to story development if using LLM
        if use_llm and ("variations" in ref_prompts or "variations" in prompts):
            self._save_prompts_to_story_markdown(scene_name, ref_prompts if ref_prompts else prompts)
            console.print(f"📚 Enhanced prompts saved to story development")
        
        # Auto-progression options
        self._offer_next_steps(scene_name, base_description)

    def _offer_next_steps(self, scene_name: str, base_description: str) -> None:
        """Offer automatic progression to next steps"""
        console.print("\n[bold yellow]🚀 What's next?[/bold yellow]")
        
        # Option 1: Generate video immediately
        if Confirm.ask("Generate Veo3 video now?", default=True):
            console.print(f"\n[bold green]Launching video generation...[/bold green]")
            console.print(f"[dim]Command: python3 tools/generate_veo3.py \"{base_description}\" --scene {scene_name}[/dim]")
            
            try:
                import subprocess
                subprocess.run([
                    'python3', 'tools/generate_veo3.py', 
                    f"{base_description} cinematic camera movement dramatic lighting",
                    '--scene', scene_name
                ])
            except Exception as e:
                console.print(f"❌ Error launching video generation: {e}")
                console.print(f"💡 Run manually: python3 tools/generate_veo3.py \"{base_description}\" --scene {scene_name}")
        
        # Option 2: Open next story clip
        next_clip = self._get_next_clip(scene_name)
        if next_clip:
            if Confirm.ask(f"Open next clip ({next_clip}) in story development?", default=True):
                console.print(f"\n[bold cyan]Opening {next_clip} for reference...[/bold cyan]")
                try:
                    import subprocess
                    subprocess.run(['open', f'07_story_development/act1_world_introduction.md'])
                except Exception as e:
                    console.print(f"💡 Manually open: 07_story_development/act1_world_introduction.md")
        
        # Option 3: Return to Control Center
        if Confirm.ask("Return to Stormlight Control Center?", default=False):
            try:
                import subprocess
                subprocess.run(['python3', 'tools/stormlight_control.py'])
            except Exception as e:
                console.print(f"💡 Run manually: python3 tools/stormlight_control.py")

    def _get_next_clip(self, current_scene: str) -> Optional[str]:
        """Determine the next clip in the sequence"""
        # Act I clip sequence mapping
        act1_sequence = [
            "title_sequence",
            "shattered_plains_reveal", 
            "kaladin_intro",
            "adolin_intro",
            "magic_system",
            "dalinar_intro",
            "spren_bonds",
            "parshendi_intro",
            "highstorm_approaching"
        ]
        
        try:
            current_index = act1_sequence.index(current_scene)
            if current_index < len(act1_sequence) - 1:
                return act1_sequence[current_index + 1]
        except ValueError:
            # Scene not in sequence, no next clip
            pass
        
        return None

    def _get_previous_clip_reference(self, current_scene: str) -> Optional[str]:
        """
        Get the end frame from the previous clip for visual consistency.
        Returns the file path to the previous clip's end frame.
        """
        # Act I sequence mapping (same as before)
        act1_sequence = [
            "title_sequence",
            "shattered_plains_reveal", 
            "kaladin_intro",
            "adolin_intro",
            "magic_system",
            "dalinar_intro",
            "spren_bonds",
            "parshendi_intro",
            "highstorm_approaching"
        ]
        
        try:
            current_index = act1_sequence.index(current_scene)
            if current_index > 0:  # Not the first clip
                prev_scene = act1_sequence[current_index - 1]
                
                # Look for the previous scene's end frame
                prev_end_frame = self.get_best_reference_image(prev_scene, "end")
                if prev_end_frame and prev_end_frame.exists():
                    return str(prev_end_frame.relative_to(self.project_root))
        except ValueError:
            # Current scene not in sequence, try to find any previous clip
            metadata = self._load_metadata()
            scene_names = list(metadata.keys())
            
            # Find scenes with end frames, get the most recent one
            for scene in reversed(scene_names):  # Most recent first
                if scene != current_scene:
                    end_frame = self.get_best_reference_image(scene, "end")
                    if end_frame and end_frame.exists():
                        return str(end_frame.relative_to(self.project_root))
        
        return None



    def detect_next_clip_from_story(self) -> Optional[tuple[str, str]]:
        """
        Parse story development files to find the next clip to work on.
        Returns (scene_name, description) tuple or None.
        Project-agnostic - works with any markdown story structure.
        """
        if not self.story_dev_dir.exists():
            return None
        
        # Look for markdown files in story development
        story_files = list(self.story_dev_dir.glob("*.md"))
        if not story_files:
            return None
        
        # Get existing scenes from metadata
        existing_scenes = set(self._load_metadata().keys())
        
        # Parse each story file for clip definitions
        for story_file in story_files:
            clips = self._parse_clips_from_markdown(story_file)
            
            # Find first clip that doesn't have styleframes yet
            for scene_name, description in clips:
                if scene_name not in existing_scenes:
                    return (scene_name, description)
        
        return None

    def _parse_clips_from_markdown(self, markdown_file: Path) -> List[tuple[str, str]]:
        """
        Dynamically parse markdown file to extract clip definitions.
        Adapts to various formats:
        - ### Clip X: Scene Name (timing)
        - **Visual**: Description or **Visual Content**: Description
        - **Simple Prompts**: "prompt text" (extracts first prompt)
        """
        clips = []
        
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # Split content into clip sections
            clip_sections = re.split(r'### Clip \d+:', content)[1:]  # Skip content before first clip
            
            for section in clip_sections:
                # Extract clip title from the first line
                lines = section.strip().split('\n')
                if not lines:
                    continue
                
                # First line should contain: Scene Name (timing)
                title_line = lines[0].strip()
                title_match = re.match(r'([^(]+)', title_line)
                if not title_match:
                    continue
                
                title = title_match.group(1).strip()
                
                # Clean up the title to create scene_name
                scene_name = title.lower()
                scene_name = re.sub(r'[^\w\s-]', '', scene_name)  # Remove special chars
                scene_name = re.sub(r'\s+', '_', scene_name)      # Replace spaces with underscores
                scene_name = scene_name.strip('_')                # Remove leading/trailing underscores
                
                # Look for visual description in various formats
                visual_desc = self._extract_visual_description(section)
                
                if scene_name and visual_desc:
                    clips.append((scene_name, visual_desc))
        
        except Exception as e:
            console.print(f"⚠️  Error parsing {markdown_file}: {e}")
        
        return clips
    
    def _extract_visual_description(self, section: str) -> str:
        """
        Extract visual description from a clip section, handling various formats.
        Priority order:
        1. **Simple Prompts**: "quoted prompt"
        2. **Visual Content**: description
        3. **Visual**: description
        4. First bullet point under visual content
        """
        import re
        
        # Try to find Simple Prompts with quoted text (highest priority)
        simple_prompt_pattern = r'\*\*Simple Prompts?\*\*:.*?"([^"]+)"'
        simple_match = re.search(simple_prompt_pattern, section, re.DOTALL | re.IGNORECASE)
        if simple_match:
            return simple_match.group(1).strip()
        
        # Try to find Visual Content (second priority)
        visual_content_pattern = r'\*\*Visual Content\*\*:\s*([^\n]+(?:\n- [^\n]+)*)'
        visual_content_match = re.search(visual_content_pattern, section, re.DOTALL)
        if visual_content_match:
            desc = visual_content_match.group(1).strip()
            # Clean up bullet points and extra whitespace
            desc = re.sub(r'\n- ', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc)
            return desc
        
        # Try to find Visual (legacy format)
        visual_pattern = r'\*\*Visual\*\*:\s*([^\n]+(?:\n- [^\n]+)*)'
        visual_match = re.search(visual_pattern, section, re.DOTALL)
        if visual_match:
            desc = visual_match.group(1).strip()
            # Clean up bullet points and extra whitespace
            desc = re.sub(r'\n- ', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc)
            return desc
        
        # Fallback: look for first bullet point after any visual-related header
        bullet_pattern = r'\*\*(?:Visual|Simple Prompts?).*?\n.*?- ([^\n]+)'
        bullet_match = re.search(bullet_pattern, section, re.DOTALL | re.IGNORECASE)
        if bullet_match:
            return bullet_match.group(1).strip()
        
        # Last resort: extract first meaningful line after title
        lines = section.strip().split('\n')[1:]  # Skip title line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('**') and not line.startswith('-'):
                return line
        
        return ""

    def suggest_next_clip(self) -> Optional[tuple[str, str]]:
        """
        Suggest the next clip to work on based on story development files.
        Returns (scene_name, description) or None.
        """
        next_clip = self.detect_next_clip_from_story()
        if next_clip:
            scene_name, description = next_clip
            console.print(f"\n[bold cyan]📖 Next clip detected from story:[/bold cyan]")
            console.print(f"[bold yellow]Scene:[/bold yellow] {scene_name}")
            console.print(f"[bold yellow]Description:[/bold yellow] {description[:100]}{'...' if len(description) > 100 else ''}")
            
            if Confirm.ask(f"Work on '{scene_name}' next?", default=True):
                return next_clip
        
        return None

    def _optimize_image(self, source_path: Path, target_path: Path) -> bool:
        """
        Optimize image: convert to JPG, resize if needed, compress
        Returns True if optimization was applied, False if just copied
        """
        if not PIL_AVAILABLE:
            # Fallback to simple copy if PIL not available
            shutil.copy2(source_path, target_path)
            return False
        
        try:
            with Image.open(source_path) as img:
                # Convert to RGB if needed (for JPG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (keep aspect ratio)
                max_dimension = 2048  # Good for Midjourney uploads
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    console.print(f"📐 Resized to {new_size[0]}x{new_size[1]}")
                
                # Save as optimized JPG
                img.save(target_path, 'JPEG', quality=90, optimize=True)
                
                # Show file size reduction
                original_size = source_path.stat().st_size / (1024 * 1024)  # MB
                new_size = target_path.stat().st_size / (1024 * 1024)  # MB
                console.print(f"📦 Optimized: {original_size:.1f}MB → {new_size:.1f}MB")
                return True
                
        except Exception as e:
            console.print(f"⚠️  Optimization failed: {e}")
            # Fallback to copy
            shutil.copy2(source_path, target_path)
            return False


def main():
    """CLI interface for styleframe manager"""
    parser = argparse.ArgumentParser(description="Manage Midjourney styleframes for video generation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Organize command
    organize_parser = subparsers.add_parser("organize", help="Organize a styleframe")
    organize_parser.add_argument("image_path", type=Path, help="Path to the image file")
    organize_parser.add_argument("scene_name", help="Scene name (e.g., kaladin_intro)")
    organize_parser.add_argument("frame_type", choices=["start", "end", "reference"], help="Type of frame")
    organize_parser.add_argument("--description", default="", help="Description of the frame")
    organize_parser.add_argument("--prompt", default="", help="Original Midjourney prompt")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List styleframes")
    list_parser.add_argument("--scene", help="Specific scene to show")
    
    # Generate prompts command
    prompts_parser = subparsers.add_parser("prompts", help="Generate Midjourney prompts")
    prompts_parser.add_argument("scene_name", help="Scene name")
    prompts_parser.add_argument("description", help="Base scene description")
    prompts_parser.add_argument("--save", action="store_true",
                               help="Save prompts to files in 02_prompts/midjourney/")
    prompts_parser.add_argument("--start-ref", help="Path to start frame for style reference")
    prompts_parser.add_argument("--llm-enhance", action="store_true",
                               help="Use LLM to enhance prompts with cinematic details")
    prompts_parser.add_argument("--variations", type=int, default=3,
                               help="Number of variations to generate (with --llm-enhance)")
    
    # Get reference command
    ref_parser = subparsers.add_parser("get-ref", help="Get best reference image for scene")
    ref_parser.add_argument("scene_name", help="Scene name")
    ref_parser.add_argument("--type", choices=["start", "end"], default="start", help="Preferred frame type")
    
    # Interactive workflow command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive workflow for complete styleframe creation")
    interactive_parser.add_argument("scene_name", nargs='?', help="Scene name (auto-detected if not provided)")
    interactive_parser.add_argument("description", nargs='?', help="Base scene description (auto-detected if not provided)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = StyleframeManager()
    
    if args.command == "organize":
        try:
            entry = manager.organize_styleframe(
                args.image_path,
                args.scene_name,
                args.frame_type,
                args.description,
                args.prompt
            )
            console.print(f"✅ Organized: {entry['path']}")
        except Exception as e:
            console.print(f"❌ Error: {e}")
    
    elif args.command == "list":
        manager.create_scene_report(args.scene)
    
    elif args.command == "prompts":
        start_ref = getattr(args, 'start_ref', None)
        use_llm = getattr(args, 'llm_enhance', False)
        variations = getattr(args, 'variations', 3)
        prompts = manager.generate_midjourney_prompts(
            args.scene_name, 
            args.description, 
            start_ref, 
            use_llm=use_llm,
            num_variations=variations
        )
        console.print(f"\n🎨 V7 Style References Prompts for {args.scene_name}:\n")
        
        # Show start frame first
        if "start_frame" in prompts:
            console.print(f"[bold green]🎬 Start Frame (Simple Content):[/bold green]")
            console.print(f"{prompts['start_frame']}\n")
        
        # Show workflow note
        if "workflow_note" in prompts:
            console.print(f"[bold yellow]📋 V7 Workflow:[/bold yellow]")
            console.print(f"{prompts['workflow_note']}\n")
        
        # Show end frame options
        console.print(f"[bold cyan]🎨 End Frame Options (Use with Style References):[/bold cyan]")
        for frame_type, prompt in prompts.items():
            if frame_type not in ["start_frame", "workflow_note", "variations"]:
                if "simple" in frame_type:
                    console.print(f"[bold green]Simple Content (Recommended):[/bold green]")
                elif "detailed" in frame_type:
                    console.print(f"[bold green]Detailed Content:[/bold green]")
                else:
                    console.print(f"[bold cyan]{frame_type.replace('_', ' ').title()}:[/bold cyan]")
                console.print(f"{prompt}\n")
        
        # Show variations if generated
        if "variations" in prompts and prompts["variations"]:
            console.print(f"[bold magenta]🔄 Variations (Different Moods):[/bold magenta]")
            for i, variation in enumerate(prompts["variations"], 1):
                console.print(f"  {i}. {variation}")
            console.print()
        
        # Save to files if requested
        if hasattr(args, 'save') and args.save:
            manager._save_prompts_to_files(args.scene_name, prompts)
    
    elif args.command == "get-ref":
        ref_path = manager.get_best_reference_image(args.scene_name, args.type)
        if ref_path:
            console.print(f"📸 Best reference for {args.scene_name}: {ref_path}")
        else:
            console.print(f"❌ No reference images found for {args.scene_name}")
    
    elif args.command == "interactive":
        scene_name = args.scene_name
        description = args.description
        
        # Auto-detect next clip if not provided
        if not scene_name or not description:
            console.print("[bold cyan]🔍 Auto-detecting next clip from story development...[/bold cyan]")
            next_clip = manager.suggest_next_clip()
            
            if next_clip:
                scene_name, description = next_clip
            else:
                # Fallback to manual input
                if not scene_name:
                    scene_name = Prompt.ask("Scene name (e.g., 'kaladin_intro')")
                if not description:
                    description = Prompt.ask("Scene description")
        
        manager.interactive_workflow(scene_name, description)


if __name__ == "__main__":
    main()
