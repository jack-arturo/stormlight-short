#!/usr/bin/env python3
"""
Prompt Generator for Stormlight: Into the Tempest
Converts story beats into Vertex AI video generation prompts
"""

import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class PromptGenerator:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.prompts_dir = self.project_root / "02_prompts"
        self.story_dir = self.project_root / "07_story_development"
        
    def load_clip_template(self, template_path: Path) -> Dict[str, Any]:
        """Load clip template from YAML file"""
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_vertex_batch(self, template_path: Path, output_path: Path = None) -> Path:
        """Generate Vertex AI batch job file from template"""
        template = self.load_clip_template(template_path)
        
        batch_jobs = []
        scene_name = template.get("scene_name", "unknown")
        clips = template.get("clips", {})
        tech_settings = template.get("technical_settings", {})
        
        for clip_id, clip_data in clips.items():
            job = {
                "scene_name": f"{scene_name}_{clip_id}",
                "prompt": clip_data["prompt"],
                "negative_prompt": clip_data.get("negative_prompt", ""),
                "duration": clip_data.get("duration", 5),
                "resolution": tech_settings.get("resolution", "1280x720"),
                "seed": None,  # Will be randomly generated
                "model": tech_settings.get("model", "veo-3-preview"),
                "temperature": tech_settings.get("temperature", 0.7),
                "guidance_scale": tech_settings.get("guidance_scale", 7.5)
            }
            batch_jobs.append(job)
        
        # Save batch configuration
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.prompts_dir / f"{scene_name}_batch_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(batch_jobs, f, indent=2)
        
        print(f"Generated batch job file: {output_path}")
        print(f"Total clips: {len(batch_jobs)}")
        
        # Calculate estimated cost
        total_seconds = sum(job["duration"] for job in batch_jobs)
        estimated_cost = total_seconds * 0.0375  # 720p rate
        print(f"Total duration: {total_seconds} seconds")
        print(f"Estimated cost: ${estimated_cost:.2f}")
        
        return output_path
    
    def generate_single_prompt(self, clip_template: Dict[str, Any], 
                             style_frame_path: Path = None) -> Dict[str, Any]:
        """Generate a single optimized prompt with style frame reference"""
        prompt = clip_template["prompt"]
        
        # Add style frame reference if available
        if style_frame_path and style_frame_path.exists():
            prompt = f"In the style of the provided reference image: {prompt}"
        
        # Enhance prompt with production notes
        if "style_notes" in clip_template:
            prompt = f"{prompt}. Style: {clip_template['style_notes']}"
        
        if "camera_movement" in clip_template:
            prompt = f"{prompt}. Camera: {clip_template['camera_movement']}"
        
        return {
            "enhanced_prompt": prompt,
            "original_prompt": clip_template["prompt"],
            "duration": clip_template.get("duration", 5),
            "style_frame": str(style_frame_path) if style_frame_path else None
        }
    
    def validate_prompts(self, template_path: Path) -> List[str]:
        """Validate prompts for common issues"""
        template = self.load_clip_template(template_path)
        issues = []
        
        clips = template.get("clips", {})
        for clip_id, clip_data in clips.items():
            prompt = clip_data.get("prompt", "")
            
            # Check prompt length
            if len(prompt) > 1000:
                issues.append(f"{clip_id}: Prompt too long ({len(prompt)} chars)")
            elif len(prompt) < 50:
                issues.append(f"{clip_id}: Prompt too short ({len(prompt)} chars)")
            
            # Check for banned words that might cause issues
            banned_words = ["gore", "violence", "blood", "explicit"]
            for word in banned_words:
                if word in prompt.lower():
                    issues.append(f"{clip_id}: Contains potentially problematic word: {word}")
            
            # Check duration
            duration = clip_data.get("duration", 0)
            if duration > 8:
                issues.append(f"{clip_id}: Duration exceeds 8 second limit ({duration}s)")
            elif duration < 3:
                issues.append(f"{clip_id}: Duration very short ({duration}s)")
        
        return issues
    
    def preview_prompts(self, template_path: Path):
        """Preview all prompts from a template"""
        template = self.load_clip_template(template_path)
        
        print(f"\n🎬 Scene: {template.get('scene_name', 'Unknown')}")
        print(f"📝 Description: {template.get('description', 'No description')}")
        print(f"\n{'='*80}\n")
        
        clips = template.get("clips", {})
        total_duration = 0
        
        for clip_id, clip_data in clips.items():
            duration = clip_data.get("duration", 5)
            total_duration += duration
            
            print(f"📹 {clip_id} ({duration}s)")
            print(f"Prompt: {clip_data.get('prompt', 'No prompt')[:200]}...")
            if "negative_prompt" in clip_data:
                print(f"Negative: {clip_data['negative_prompt']}")
            if "style_notes" in clip_data:
                print(f"Style: {clip_data['style_notes']}")
            print(f"{'-'*80}\n")
        
        print(f"Total clips: {len(clips)}")
        print(f"Total duration: {total_duration} seconds")
        print(f"Estimated cost (720p): ${total_duration * 0.0375:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Generate Vertex AI prompts from story templates")
    parser.add_argument("--template", required=True, help="Path to clip template YAML")
    parser.add_argument("--batch", action="store_true", help="Generate batch job file")
    parser.add_argument("--preview", action="store_true", help="Preview prompts")
    parser.add_argument("--validate", action="store_true", help="Validate prompts")
    parser.add_argument("--output", help="Output path for batch file")
    
    args = parser.parse_args()
    
    generator = PromptGenerator()
    template_path = Path(args.template)
    
    if not template_path.exists():
        print(f"Template not found: {template_path}")
        return
    
    if args.validate:
        issues = generator.validate_prompts(template_path)
        if issues:
            print("⚠️  Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All prompts validated successfully!")
    
    elif args.preview:
        generator.preview_prompts(template_path)
    
    elif args.batch:
        output_path = Path(args.output) if args.output else None
        batch_path = generator.generate_vertex_batch(template_path, output_path)
        print(f"\n✅ Batch file ready: {batch_path}")
        print("\nTo submit this batch:")
        print(f"python3 tools/vertex_manager.py --batch-config {batch_path} --project-id stormlight-short")
    
    else:
        generator.preview_prompts(template_path)


if __name__ == "__main__":
    main()
