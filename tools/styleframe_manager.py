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
    
    def generate_midjourney_prompts(self, scene_name: str, base_description: str) -> Dict[str, str]:
        """
        Generate clean Midjourney prompts optimized for --style raw
        
        Args:
            scene_name: Scene identifier
            base_description: Base scene description
        """
        return self._generate_raw_prompts(scene_name, base_description)
    

    
    def _generate_raw_prompts(self, scene_name: str, base_description: str) -> Dict[str, str]:
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
                "start": "empty sky ready for title",
                "end": "elegant title text STORMLIGHT INTO THE TEMPEST prominently displayed"
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
        
        prompts = {
            "start_frame": f"{base_description} {variations['start']} {style_keywords} dramatic lighting Arcane style by Fortiche --style raw --ar 16:9 --q 2",
            "end_frame": f"{base_description} {variations['end']} {style_keywords} dramatic lighting Arcane style by Fortiche --style raw --ar 16:9 --q 2"
        }
        
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
            
            for frame_type, prompt in prompts.items():
                f.write(f"{frame_type.replace('_', ' ').title()}:\n")
                f.write(f"{prompt}\n\n")
        
        console.print(f"💾 Saved: {filepath}")


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
    
    # Get reference command
    ref_parser = subparsers.add_parser("get-ref", help="Get best reference image for scene")
    ref_parser.add_argument("scene_name", help="Scene name")
    ref_parser.add_argument("--type", choices=["start", "end"], default="start", help="Preferred frame type")
    
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
        prompts = manager.generate_midjourney_prompts(args.scene_name, args.description)
        console.print(f"\n🎨 Midjourney Prompts for {args.scene_name}:\n")
        
        for frame_type, prompt in prompts.items():
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


if __name__ == "__main__":
    main()
