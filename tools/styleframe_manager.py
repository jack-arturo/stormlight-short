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
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = image_path.suffix
        new_filename = f"{scene_name}_{frame_type}_{timestamp}{file_extension}"
        target_path = scene_dir / new_filename
        
        # Copy the file
        shutil.copy2(image_path, target_path)
        
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
    
    def generate_midjourney_prompts(self, scene_name: str, base_description: str, start_frame_path: str = None) -> Dict[str, str]:
        """
        Generate clean Midjourney prompts optimized for --style raw
        
        Args:
            scene_name: Scene identifier
            base_description: Base scene description
            start_frame_path: Path to start frame for style reference (optional)
        """
        return self._generate_raw_prompts(scene_name, base_description, start_frame_path)
    

    
    def _generate_raw_prompts(self, scene_name: str, base_description: str, start_frame_path: str = None) -> Dict[str, str]:
        """Generate clean prompts optimized for --style raw"""
        
        # Scene-specific style keywords (minimal)
        scene_styles = {
            "kaladin": "stormy dramatic navy gray",
            "bridge": "action earth tones dust",
            "highstorm": "electric blue storm massive",
            "shattered_plains": "alien crystal desolate",
            "spren": "ethereal glowing mystical",
            "title": "epic cinematic storm"
        }
        
        # Scene-specific start/end variations
        scene_variations = {
            "title_sequence": {
                "start": "empty sky with dramatic clouds, clear space for title overlay",
                "end": "same composition with dramatic sky, clear central area for title overlay"
            },
            "kaladin_intro": {
                "start": "close-up focus on face and expression",
                "end": "wider shot showing full context and environment"
            },
            "adolin_intro": {
                "start": "confident stance in training position",
                "end": "mid-sword technique demonstration"
            },
            "dalinar_intro": {
                "start": "studying maps with intense concentration",
                "end": "looking up with commanding presence"
            },
            "shattered_plains": {
                "start": "high aerial view showing plateau tops",
                "end": "diving down into chasm depths with mist"
            }
        }
        
        # Determine scene style
        style_keywords = "epic cinematic"  # default
        for keyword, style in scene_styles.items():
            if keyword in scene_name.lower():
                style_keywords = style
                break
        
        # Get scene-specific variations or use defaults
        variations = scene_variations.get(scene_name, {
            "start": "establishing shot",
            "end": "closer detailed view"
        })
        
        # Base prompt components with text avoidance (simplified to avoid weight conflicts)
        text_avoidance = "--no text --no typography"
        base_prompt = f"{base_description} {style_keywords} dramatic lighting Arcane style by Fortiche {text_avoidance} --style raw --ar 16:9 --q 2"
        
        prompts = {
            "start_frame": f"{base_description} {variations['start']} {style_keywords} dramatic lighting Arcane style by Fortiche {text_avoidance} --style raw --ar 16:9 --q 2"
        }
        
        # End frame uses start frame as style reference if available
        if start_frame_path:
            prompts["end_frame_variation"] = f"{variations['end']} {style_keywords} dramatic lighting {text_avoidance}"
            prompts["end_frame_full"] = f"{base_description} {variations['end']} {style_keywords} dramatic lighting Arcane style by Fortiche {text_avoidance} --style raw --ar 16:9 --q 2"
            prompts["workflow_note"] = "EDITOR WORKFLOW: 1) Generate start frame, 2) Upload to Midjourney web UI, 3) Click 'Edit', 4) Use 'Erase/Smart Erase' on sky area, 5) Submit Edit with variation prompt. Text added in post-production."
        else:
            prompts["end_frame"] = f"{base_description} {variations['end']} {style_keywords} dramatic lighting Arcane style by Fortiche {text_avoidance} --style raw --ar 16:9 --q 2"
            prompts["workflow_note"] = "WORKFLOW: 1) Generate start frame first, 2) Use Midjourney Editor to erase sky area and add title space. Text will be added in post-production."
        
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
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Always show start frame first and clearly
            if "start_frame" in prompts:
                f.write("🎬 STEP 1 - Generate Start Frame:\n")
                f.write(f"{prompts['start_frame']}\n\n")
            
            # Show workflow note
            if "workflow_note" in prompts:
                f.write("📋 Next Steps:\n")
                f.write(f"{prompts['workflow_note']}\n\n")
            
            # Show other prompts for reference
            f.write("📝 Reference (for later steps):\n")
            for frame_type, prompt in prompts.items():
                if frame_type not in ["start_frame", "workflow_note"]:
                    f.write(f"{frame_type.replace('_', ' ').title()}:\n")
                    f.write(f"{prompt}\n\n")
        
        console.print(f"💾 Saved: {filepath}")

    def interactive_workflow(self, scene_name: str, base_description: str) -> None:
        """Interactive workflow that walks user through the entire process"""
        console.print(Panel.fit(
            f"🎬 Interactive Styleframe Workflow for [bold cyan]{scene_name}[/bold cyan]",
            style="bold blue"
        ))
        
        # Step 1: Generate prompts
        console.print("\n[bold yellow]Step 1: Generating Midjourney prompts...[/bold yellow]")
        prompts = self.generate_midjourney_prompts(scene_name, base_description)
        
        # Display start frame prompt (plain text for easy copying)
        console.print("\n[bold green]🎨 Copy this prompt to Midjourney:[/bold green]")
        console.print("=" * 80)
        console.print(prompts["start_frame"])
        console.print("=" * 80)
        
        # Wait for user to generate start frame
        console.print("\n[bold yellow]Step 2: Generate your start frame[/bold yellow]")
        console.print("1. Copy the prompt above")
        console.print("2. Paste it into Midjourney")
        console.print("3. Generate and save your favorite result")
        
        if not Confirm.ask("\nHave you generated and saved your start frame?"):
            console.print("❌ Come back when you have your start frame ready!")
            return
        
        # Step 3: Organize start frame
        console.print("\n[bold yellow]Step 3: Organize your start frame[/bold yellow]")
        console.print("💡 Save your image to tmp/tmp.jpg for quick workflow (smaller file size)")
        
        # Default to tmp/tmp.jpg, but allow override
        default_path = "tmp/tmp.jpg"
        if Path(default_path).exists():
            if Confirm.ask(f"Use {default_path}?", default=True):
                start_frame_path = Path(default_path)
            else:
                start_frame_path = Path(Prompt.ask("Enter the path to your start frame image"))
        else:
            console.print(f"❌ {default_path} not found")
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
        
        # Step 4: Generate end frame with style reference
        console.print("\n[bold yellow]Step 4: Generate matching end frame[/bold yellow]")
        console.print("Now we'll create an end frame that perfectly matches your start frame style.")
        
        # Generate prompts with start frame reference
        ref_prompts = self.generate_midjourney_prompts(scene_name, base_description, str(entry['path']))
        
        console.print("\n[bold cyan]Midjourney Editor Workflow:[/bold cyan]")
        console.print("1. Go to Midjourney web UI and upload your start frame")
        console.print("2. Click 'Edit' to open the Editor")
        console.print("3. Use 'Erase' or 'Smart Erase' tool to select the sky area where you want the title")
        console.print("4. Click 'Submit Edit' and use this prompt:")
        
        if "end_frame_variation" in ref_prompts:
            console.print("\n[bold green]🎨 Editor Prompt:[/bold green]")
            console.print("=" * 60)
            console.print(ref_prompts["end_frame_variation"])
            console.print("=" * 60)
        
        console.print("\n[bold yellow]💡 Optional Tools:[/bold yellow]")
        console.print("• Use 'Pan' to adjust framing if needed")
        console.print("• Use 'Zoom Out' for wider composition")
        console.print("• Use 'Crop' to fine-tune the aspect ratio")
        console.print("• All tools can be combined with 'Remix' for variations")
        
        # Wait for end frame generation
        if not Confirm.ask("\nHave you generated your end frame?"):
            console.print("💾 Prompts saved to file for later use")
            self._save_prompts_to_files(scene_name, ref_prompts)
            return
        
        # Step 5: Organize end frame
        console.print("\n[bold yellow]Step 5: Organize your end frame[/bold yellow]")
        console.print("💡 Save your end frame to tmp/tmp.jpg and confirm")
        
        # Default to tmp/tmp.jpg for end frame too
        default_path = "tmp/tmp.jpg"
        if Path(default_path).exists():
            if Confirm.ask(f"Use {default_path} for end frame?", default=True):
                end_frame_path = Path(default_path)
            else:
                end_frame_path = Path(Prompt.ask("Enter the path to your end frame image"))
        else:
            console.print(f"❌ {default_path} not found")
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
    
    # Get reference command
    ref_parser = subparsers.add_parser("get-ref", help="Get best reference image for scene")
    ref_parser.add_argument("scene_name", help="Scene name")
    ref_parser.add_argument("--type", choices=["start", "end"], default="start", help="Preferred frame type")
    
    # Interactive workflow command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive workflow for complete styleframe creation")
    interactive_parser.add_argument("scene_name", help="Scene name")
    interactive_parser.add_argument("description", help="Base scene description")
    
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
        prompts = manager.generate_midjourney_prompts(args.scene_name, args.description, start_ref)
        console.print(f"\n🎨 Midjourney Prompts for {args.scene_name}:\n")
        
        for frame_type, prompt in prompts.items():
            if frame_type == "workflow_note":
                console.print(f"[bold yellow]📋 {prompt}[/bold yellow]\n")
            else:
                console.print(f"[bold cyan]{frame_type.replace('_', ' ').title()}:[/bold cyan]")
                console.print(f"{prompt}\n")
        
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
        manager.interactive_workflow(args.scene_name, args.description)


if __name__ == "__main__":
    main()
