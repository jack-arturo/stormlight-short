#!/usr/bin/env python3
"""
Flow Integration Manager for Stormlight Short
Handles Flow exports, take numbering, and prompt synchronization.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib


class FlowManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.flow_exports_dir = self.project_root / "04_flow_exports"
        self.prompts_dir = self.project_root / "02_prompts"
        
        # Ensure directories exist
        self.flow_exports_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
    
    def organize_flow_export(self, source_file: Path, scene_name: str, 
                           prompt_text: str, seed: Optional[int] = None,
                           metadata: Dict[str, Any] = None) -> Path:
        """Organize Flow export with proper naming and metadata"""
        
        # Generate take number
        take_number = self._get_next_take_number(scene_name)
        
        # Create scene directory
        scene_dir = self.flow_exports_dir / scene_name
        scene_dir.mkdir(exist_ok=True)
        
        # Generate filename with take number and seed
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_suffix = f"_seed{seed}" if seed else ""
        file_extension = source_file.suffix
        
        target_filename = f"{scene_name}_take{take_number:02d}_{timestamp}{seed_suffix}{file_extension}"
        target_path = scene_dir / target_filename
        
        # Copy the file
        shutil.copy2(source_file, target_path)
        print(f"Copied Flow export: {source_file} -> {target_path}")
        
        # Save metadata
        self._save_flow_metadata(target_path, prompt_text, seed, metadata, take_number)
        
        # Update prompt ledger
        self._update_prompt_ledger(scene_name, take_number, prompt_text, seed, metadata)
        
        return target_path
    
    def _get_next_take_number(self, scene_name: str) -> int:
        """Get the next take number for a scene"""
        scene_dir = self.flow_exports_dir / scene_name
        if not scene_dir.exists():
            return 1
            
        # Find existing takes
        existing_takes = []
        for file in scene_dir.glob(f"{scene_name}_take*"):
            try:
                # Extract take number from filename
                parts = file.stem.split("_take")
                if len(parts) > 1:
                    take_part = parts[1].split("_")[0]
                    take_num = int(take_part)
                    existing_takes.append(take_num)
            except (ValueError, IndexError):
                continue
                
        return max(existing_takes, default=0) + 1
    
    def _save_flow_metadata(self, target_path: Path, prompt_text: str, 
                          seed: Optional[int], metadata: Dict[str, Any], 
                          take_number: int):
        """Save comprehensive metadata for Flow export"""
        
        metadata_dict = {
            "timestamp": datetime.now().isoformat(),
            "source": "Flow",
            "take_number": take_number,
            "prompt_text": prompt_text,
            "seed": seed,
            "file_path": str(target_path),
            "file_hash": self._calculate_file_hash(target_path),
            "metadata": metadata or {}
        }
        
        # Save metadata as JSON
        metadata_path = target_path.with_suffix(target_path.suffix + ".meta.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)
            
        print(f"Saved metadata: {metadata_path}")
    
    def _update_prompt_ledger(self, scene_name: str, take_number: int, 
                            prompt_text: str, seed: Optional[int], 
                            metadata: Dict[str, Any]):
        """Update the prompt ledger with new entry"""
        
        ledger_path = self.prompts_dir / f"{scene_name}_ledger.json"
        
        # Load existing ledger or create new
        if ledger_path.exists():
            with open(ledger_path, "r") as f:
                ledger = json.load(f)
        else:
            ledger = {
                "scene_name": scene_name,
                "created": datetime.now().isoformat(),
                "entries": []
            }
        
        # Add new entry
        entry = {
            "take_number": take_number,
            "timestamp": datetime.now().isoformat(),
            "prompt_text": prompt_text,
            "seed": seed,
            "source": "Flow",
            "metadata": metadata or {}
        }
        
        ledger["entries"].append(entry)
        ledger["updated"] = datetime.now().isoformat()
        
        # Save updated ledger
        with open(ledger_path, "w") as f:
            json.dump(ledger, f, indent=2)
            
        print(f"Updated prompt ledger: {ledger_path}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for integrity checking"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def batch_organize_exports(self, source_dir: Path, scene_mapping: Dict[str, Dict]) -> List[Path]:
        """Batch organize multiple Flow exports"""
        organized_files = []
        
        for file_path in source_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Try to match file to scene
                scene_name = self._detect_scene_from_filename(file_path.name, scene_mapping)
                
                if scene_name and scene_name in scene_mapping:
                    scene_info = scene_mapping[scene_name]
                    prompt_text = scene_info.get("prompt", "")
                    seed = scene_info.get("seed")
                    metadata = scene_info.get("metadata", {})
                    
                    organized_path = self.organize_flow_export(
                        file_path, scene_name, prompt_text, seed, metadata
                    )
                    organized_files.append(organized_path)
                else:
                    print(f"Warning: Could not determine scene for {file_path}")
        
        return organized_files
    
    def _detect_scene_from_filename(self, filename: str, scene_mapping: Dict) -> Optional[str]:
        """Detect scene name from filename using scene mapping"""
        filename_lower = filename.lower()
        
        for scene_name in scene_mapping.keys():
            if scene_name.lower() in filename_lower:
                return scene_name
                
        return None


def main():
    """CLI interface for Flow management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Flow Export Manager")
    parser.add_argument("--source", required=True, help="Source file or directory")
    parser.add_argument("--scene", required=True, help="Scene name")
    parser.add_argument("--prompt", required=True, help="Prompt text")
    parser.add_argument("--seed", type=int, help="Seed value")
    parser.add_argument("--metadata", help="Additional metadata as JSON string")
    
    args = parser.parse_args()
    
    manager = FlowManager()
    source_path = Path(args.source)
    
    # Parse metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("Warning: Invalid metadata JSON, ignoring")
    
    if source_path.is_file():
        # Single file
        organized_path = manager.organize_flow_export(
            source_path, args.scene, args.prompt, args.seed, metadata
        )
        print(f"Organized: {organized_path}")
    else:
        print("Batch organization not implemented in CLI yet")


if __name__ == "__main__":
    main()
