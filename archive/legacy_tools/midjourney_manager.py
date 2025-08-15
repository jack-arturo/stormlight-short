#!/usr/bin/env python3
"""
Midjourney Style Frame Manager for Stormlight Short
Handles batch uploads, proper naming, and metadata tracking.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import hashlib


class MidjourneyManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.styleframes_dir = self.project_root / "01_styleframes_midjourney"
        self.prompts_dir = self.project_root / "02_prompts"
        
        # Ensure directories exist
        self.styleframes_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Required specs
        self.min_resolution = (1280, 720)
        self.target_aspect_ratio = 16/9
        self.tolerance = 0.1  # 10% tolerance for aspect ratio
    
    def validate_image(self, image_path: Path) -> Tuple[bool, str]:
        """Validate image meets requirements (16:9, ≥1280×720)"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                # Check minimum resolution
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    return False, f"Resolution {width}x{height} below minimum {self.min_resolution[0]}x{self.min_resolution[1]}"
                
                # Check aspect ratio (with tolerance)
                if abs(aspect_ratio - self.target_aspect_ratio) > self.tolerance:
                    return False, f"Aspect ratio {aspect_ratio:.2f} not close to 16:9 ({self.target_aspect_ratio:.2f})"
                
                return True, f"Valid: {width}x{height}, aspect ratio {aspect_ratio:.2f}"
                
        except Exception as e:
            return False, f"Error reading image: {e}"
    
    def extract_seed_from_filename(self, filename: str) -> Optional[int]:
        """Extract seed from Midjourney filename patterns"""
        # Common Midjourney patterns
        patterns = [
            r'--seed\s+(\d+)',
            r'seed_(\d+)',
            r'_(\d+)\.png$',
            r'_(\d+)\.jpg$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def organize_styleframe(self, source_file: Path, scene_name: str, 
                          descriptor: str, prompt_text: str = "",
                          seed: Optional[int] = None, 
                          metadata: Dict[str, Any] = None) -> Optional[Path]:
        """Organize a single style frame with proper naming and validation"""
        
        # Validate image first
        is_valid, message = self.validate_image(source_file)
        if not is_valid:
            print(f"Warning: {source_file.name} - {message}")
            # Could optionally resize/crop here
        
        # Extract seed if not provided
        if seed is None:
            seed = self.extract_seed_from_filename(source_file.name)
        
        # Create scene directory
        scene_dir = self.styleframes_dir / scene_name
        scene_dir.mkdir(exist_ok=True)
        
        # Generate proper filename: {scene}_{descriptor}_{seed}.png
        seed_suffix = f"_{seed}" if seed else "_noseed"
        target_filename = f"{scene_name}_{descriptor}{seed_suffix}.png"
        target_path = scene_dir / target_filename
        
        # Handle duplicates
        counter = 1
        while target_path.exists():
            target_filename = f"{scene_name}_{descriptor}{seed_suffix}_v{counter}.png"
            target_path = scene_dir / target_filename
            counter += 1
        
        # Copy file (convert to PNG if needed)
        if source_file.suffix.lower() == '.png':
            shutil.copy2(source_file, target_path)
        else:
            # Convert to PNG
            with Image.open(source_file) as img:
                img.save(target_path, 'PNG')
        
        print(f"Organized style frame: {source_file.name} -> {target_path.name}")
        
        # Save metadata
        self._save_styleframe_metadata(target_path, prompt_text, seed, metadata, descriptor)
        
        # Update prompt ledger
        if prompt_text:
            self._update_prompt_ledger(scene_name, descriptor, prompt_text, seed, metadata)
        
        return target_path
    
    def _save_styleframe_metadata(self, target_path: Path, prompt_text: str,
                                seed: Optional[int], metadata: Dict[str, Any],
                                descriptor: str):
        """Save comprehensive metadata for style frame"""
        
        # Get image info
        with Image.open(target_path) as img:
            width, height = img.size
            aspect_ratio = width / height
        
        metadata_dict = {
            "timestamp": datetime.now().isoformat(),
            "source": "Midjourney",
            "descriptor": descriptor,
            "prompt_text": prompt_text,
            "seed": seed,
            "file_path": str(target_path),
            "file_hash": self._calculate_file_hash(target_path),
            "image_info": {
                "width": width,
                "height": height,
                "aspect_ratio": round(aspect_ratio, 3),
                "format": "PNG"
            },
            "validation": {
                "meets_requirements": width >= self.min_resolution[0] and height >= self.min_resolution[1],
                "aspect_ratio_valid": abs(aspect_ratio - self.target_aspect_ratio) <= self.tolerance
            },
            "metadata": metadata or {}
        }
        
        # Save metadata as JSON
        metadata_path = target_path.with_suffix('.meta.json')
        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)
    
    def _update_prompt_ledger(self, scene_name: str, descriptor: str, 
                            prompt_text: str, seed: Optional[int],
                            metadata: Dict[str, Any]):
        """Update prompt ledger for style frames"""
        
        ledger_path = self.prompts_dir / f"{scene_name}_styleframes_ledger.json"
        
        # Load existing ledger or create new
        if ledger_path.exists():
            with open(ledger_path, "r") as f:
                ledger = json.load(f)
        else:
            ledger = {
                "scene_name": scene_name,
                "type": "styleframes",
                "created": datetime.now().isoformat(),
                "entries": []
            }
        
        # Add new entry
        entry = {
            "descriptor": descriptor,
            "timestamp": datetime.now().isoformat(),
            "prompt_text": prompt_text,
            "seed": seed,
            "source": "Midjourney",
            "metadata": metadata or {}
        }
        
        ledger["entries"].append(entry)
        ledger["updated"] = datetime.now().isoformat()
        
        # Save updated ledger
        with open(ledger_path, "w") as f:
            json.dump(ledger, f, indent=2)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def batch_organize_styleframes(self, source_dir: Path, 
                                 scene_mapping: Dict[str, Dict]) -> List[Path]:
        """Batch organize multiple style frames"""
        organized_files = []
        
        # Supported image formats
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        
        for file_path in source_dir.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix.lower() in image_extensions and 
                not file_path.name.startswith('.')):
                
                # Try to match file to scene
                scene_name = self._detect_scene_from_filename(file_path.name, scene_mapping)
                
                if scene_name and scene_name in scene_mapping:
                    scene_info = scene_mapping[scene_name]
                    descriptor = scene_info.get("descriptor", "frame")
                    prompt_text = scene_info.get("prompt", "")
                    seed = scene_info.get("seed")
                    metadata = scene_info.get("metadata", {})
                    
                    organized_path = self.organize_styleframe(
                        file_path, scene_name, descriptor, prompt_text, seed, metadata
                    )
                    if organized_path:
                        organized_files.append(organized_path)
                else:
                    print(f"Warning: Could not determine scene for {file_path}")
        
        return organized_files
    
    def _detect_scene_from_filename(self, filename: str, scene_mapping: Dict) -> Optional[str]:
        """Detect scene name from filename"""
        filename_lower = filename.lower()
        
        for scene_name in scene_mapping.keys():
            if scene_name.lower() in filename_lower:
                return scene_name
        
        return None
    
    def resize_for_requirements(self, image_path: Path, output_path: Path = None) -> Path:
        """Resize/crop image to meet 16:9 requirements"""
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_resized.png"
        
        with Image.open(image_path) as img:
            width, height = img.size
            current_ratio = width / height
            
            if abs(current_ratio - self.target_aspect_ratio) <= self.tolerance:
                # Already correct ratio, just ensure minimum size
                if width >= self.min_resolution[0] and height >= self.min_resolution[1]:
                    img.save(output_path, 'PNG')
                    return output_path
                else:
                    # Scale up maintaining ratio
                    scale = max(self.min_resolution[0] / width, self.min_resolution[1] / height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    img_resized.save(output_path, 'PNG')
                    return output_path
            else:
                # Need to crop to 16:9
                if current_ratio > self.target_aspect_ratio:
                    # Too wide, crop width
                    new_width = int(height * self.target_aspect_ratio)
                    left = (width - new_width) // 2
                    img_cropped = img.crop((left, 0, left + new_width, height))
                else:
                    # Too tall, crop height
                    new_height = int(width / self.target_aspect_ratio)
                    top = (height - new_height) // 2
                    img_cropped = img.crop((0, top, width, top + new_height))
                
                # Ensure minimum resolution
                crop_width, crop_height = img_cropped.size
                if crop_width < self.min_resolution[0] or crop_height < self.min_resolution[1]:
                    scale = max(self.min_resolution[0] / crop_width, self.min_resolution[1] / crop_height)
                    new_width = int(crop_width * scale)
                    new_height = int(crop_height * scale)
                    img_cropped = img_cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                img_cropped.save(output_path, 'PNG')
                return output_path


def main():
    """CLI interface for Midjourney management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Midjourney Style Frame Manager")
    parser.add_argument("--source", required=True, help="Source file or directory")
    parser.add_argument("--scene", required=True, help="Scene name")
    parser.add_argument("--descriptor", required=True, help="Frame descriptor")
    parser.add_argument("--prompt", help="Prompt text")
    parser.add_argument("--seed", type=int, help="Seed value")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't organize")
    parser.add_argument("--resize", action="store_true", help="Resize to meet requirements")
    
    args = parser.parse_args()
    
    manager = MidjourneyManager()
    source_path = Path(args.source)
    
    if args.validate_only:
        is_valid, message = manager.validate_image(source_path)
        print(f"{source_path.name}: {message}")
        return
    
    if args.resize:
        resized_path = manager.resize_for_requirements(source_path)
        print(f"Resized: {resized_path}")
        return
    
    if source_path.is_file():
        organized_path = manager.organize_styleframe(
            source_path, args.scene, args.descriptor, 
            args.prompt or "", args.seed
        )
        if organized_path:
            print(f"Organized: {organized_path}")
    else:
        print("Batch organization requires scene mapping configuration")


if __name__ == "__main__":
    main()
