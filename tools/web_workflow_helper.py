#!/usr/bin/env python3
"""
Web Workflow Helper for Vertex AI Media Studio
Assists with organizing downloaded clips and logging prompts
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
import shutil

class WebWorkflowHelper:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.flow_exports_dir = self.project_root / "04_flow_exports"
        self.prompts_dir = self.project_root / "02_prompts"
        self.ledger_file = self.prompts_dir / "ledger.jsonl"
        
        # Ensure directories exist
        self.flow_exports_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
    
    def organize_downloaded_clip(self, 
                               source_file: Path, 
                               scene_name: str, 
                               prompt: str,
                               take_number: int = None,
                               notes: str = "") -> Dict[str, Any]:
        """
        Organize a downloaded clip into the project structure
        
        Args:
            source_file: Path to downloaded MP4 file
            scene_name: Scene identifier (e.g., 'title_sequence', 'kaladin_intro')
            prompt: Full prompt text used for generation
            take_number: Take number (auto-incremented if None)
            notes: Optional notes about the generation
            
        Returns:
            Dictionary with organization results
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        # Auto-increment take number if not provided
        if take_number is None:
            take_number = self._get_next_take_number(scene_name)
        
        # Generate timestamp
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create target filename
        target_filename = f"{scene_name}_take{take_number:02d}_{timestamp_str}.mp4"
        target_path = self.flow_exports_dir / target_filename
        
        # Copy file to target location
        shutil.copy2(source_file, target_path)
        
        # Calculate file hash for integrity
        file_hash = self._calculate_file_hash(target_path)
        
        # Get video metadata
        duration = self._get_video_duration(target_path)
        file_size = target_path.stat().st_size
        
        # Create ledger entry
        ledger_entry = {
            "timestamp": timestamp.isoformat(),
            "scene": scene_name,
            "take": take_number,
            "prompt": prompt,
            "duration": duration,
            "resolution": "720p",  # Veo 3 preview default
            "model": "veo-3.0-generate-preview",
            "quality": "high",
            "filename": target_filename,
            "file_hash": file_hash,
            "file_size_bytes": file_size,
            "notes": notes
        }
        
        # Append to ledger
        self._append_to_ledger(ledger_entry)
        
        print(f"✅ Organized clip: {target_filename}")
        print(f"📝 Added to ledger: {scene_name} take {take_number}")
        
        return {
            "success": True,
            "target_path": target_path,
            "ledger_entry": ledger_entry,
            "take_number": take_number
        }
    
    def _get_next_take_number(self, scene_name: str) -> int:
        """Get the next take number for a scene"""
        existing_takes = []
        
        # Check existing files
        for file_path in self.flow_exports_dir.glob(f"{scene_name}_take*.mp4"):
            try:
                # Extract take number from filename
                parts = file_path.stem.split('_')
                for part in parts:
                    if part.startswith('take'):
                        take_num = int(part[4:])  # Remove 'take' prefix
                        existing_takes.append(take_num)
                        break
            except (ValueError, IndexError):
                continue
        
        return max(existing_takes, default=0) + 1
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for integrity checking"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_video_duration(self, file_path: Path) -> int:
        """Get video duration in seconds (simplified - returns 8 for now)"""
        # TODO: Use ffprobe or similar to get actual duration
        # For now, assume 8 seconds (Veo 3 preview max)
        return 8
    
    def _append_to_ledger(self, entry: Dict[str, Any]):
        """Append entry to the JSONL ledger file"""
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def list_scenes(self) -> Dict[str, int]:
        """List all scenes and their take counts"""
        scenes = {}
        
        for file_path in self.flow_exports_dir.glob("*.mp4"):
            try:
                scene_name = file_path.stem.split('_take')[0]
                scenes[scene_name] = scenes.get(scene_name, 0) + 1
            except IndexError:
                continue
        
        return scenes
    
    def get_scene_prompts(self, scene_name: str) -> list:
        """Get all prompts used for a specific scene"""
        prompts = []
        
        if not self.ledger_file.exists():
            return prompts
        
        with open(self.ledger_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('scene') == scene_name:
                        prompts.append({
                            'take': entry.get('take'),
                            'prompt': entry.get('prompt'),
                            'timestamp': entry.get('timestamp'),
                            'notes': entry.get('notes', '')
                        })
                except json.JSONDecodeError:
                    continue
        
        return sorted(prompts, key=lambda x: x['take'])
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate a status report of all clips and progress"""
        scenes = self.list_scenes()
        total_clips = sum(scenes.values())
        
        # Target scenes from story development
        target_scenes = [
            "title_sequence", "kaladin_intro", "shattered_plains", "bridge_run", 
            "highstorm", "adolin_intro", "dalinar_command", "spren_encounter",
            "kaladin_leadership", "parshendi_warriors", "first_surgebinding",
            "syl_true_form", "first_oath", "knights_radiant", "series_hook"
        ]
        
        progress = {
            "total_clips_generated": total_clips,
            "target_clips": len(target_scenes),
            "completion_percentage": (total_clips / len(target_scenes)) * 100,
            "scenes_by_take_count": scenes,
            "missing_scenes": [scene for scene in target_scenes if scene not in scenes],
            "ledger_entries": self._count_ledger_entries()
        }
        
        return progress
    
    def _count_ledger_entries(self) -> int:
        """Count total entries in ledger"""
        if not self.ledger_file.exists():
            return 0
        
        count = 0
        with open(self.ledger_file, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

def main():
    """Command line interface for web workflow helper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vertex AI Media Studio Web Workflow Helper")
    parser.add_argument("command", choices=["organize", "status", "scenes", "prompts"], 
                       help="Command to execute")
    
    # Arguments for organize command
    parser.add_argument("--source", type=Path, help="Source MP4 file to organize")
    parser.add_argument("--scene", help="Scene name (e.g., title_sequence)")
    parser.add_argument("--prompt", help="Prompt text used for generation")
    parser.add_argument("--take", type=int, help="Take number (auto-incremented if not provided)")
    parser.add_argument("--notes", default="", help="Optional notes about the generation")
    
    # Arguments for prompts command
    parser.add_argument("--scene-name", help="Scene name to get prompts for")
    
    args = parser.parse_args()
    
    helper = WebWorkflowHelper()
    
    if args.command == "organize":
        if not all([args.source, args.scene, args.prompt]):
            print("❌ Error: organize command requires --source, --scene, and --prompt")
            sys.exit(1)
        
        try:
            result = helper.organize_downloaded_clip(
                source_file=args.source,
                scene_name=args.scene,
                prompt=args.prompt,
                take_number=args.take,
                notes=args.notes
            )
            print(f"✅ Success: {result['target_path']}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "status":
        report = helper.generate_status_report()
        print("\n📊 Stormlight Clips Status Report")
        print("=" * 40)
        print(f"Total clips generated: {report['total_clips_generated']}")
        print(f"Target clips: {report['target_clips']}")
        print(f"Completion: {report['completion_percentage']:.1f}%")
        print(f"Ledger entries: {report['ledger_entries']}")
        
        if report['scenes_by_take_count']:
            print("\n🎬 Scenes by take count:")
            for scene, count in sorted(report['scenes_by_take_count'].items()):
                print(f"  {scene}: {count} take{'s' if count != 1 else ''}")
        
        if report['missing_scenes']:
            print(f"\n⏳ Missing scenes ({len(report['missing_scenes'])}):")
            for scene in report['missing_scenes'][:5]:  # Show first 5
                print(f"  - {scene}")
            if len(report['missing_scenes']) > 5:
                print(f"  ... and {len(report['missing_scenes']) - 5} more")
    
    elif args.command == "scenes":
        scenes = helper.list_scenes()
        if scenes:
            print("\n🎬 Generated Scenes:")
            for scene, count in sorted(scenes.items()):
                print(f"  {scene}: {count} take{'s' if count != 1 else ''}")
        else:
            print("No scenes found. Start generating clips!")
    
    elif args.command == "prompts":
        if not args.scene_name:
            print("❌ Error: prompts command requires --scene-name")
            sys.exit(1)
        
        prompts = helper.get_scene_prompts(args.scene_name)
        if prompts:
            print(f"\n📝 Prompts for {args.scene_name}:")
            for p in prompts:
                print(f"\n  Take {p['take']} ({p['timestamp']}):")
                print(f"    Prompt: {p['prompt']}")
                if p['notes']:
                    print(f"    Notes: {p['notes']}")
        else:
            print(f"No prompts found for scene: {args.scene_name}")

if __name__ == "__main__":
    main()
