#!/usr/bin/env python3
"""
Gemini API Veo 3 Video Generation for Stormlight Archives
Generates high-quality 720p, 8-second videos using veo-3.0-generate-preview
"""

import os
import time
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

class Veo3Generator:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.flow_exports_dir = self.project_root / "04_flow_exports"
        self.prompts_dir = self.project_root / "02_prompts"
        self.ledger_file = self.prompts_dir / "ledger.jsonl"
        
        # Ensure directories exist
        self.flow_exports_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Configure Gemini API
        self._setup_api()
    
    def _setup_api(self):
        """Set up Gemini API authentication"""
        # Try to get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            # Try to get from Google Cloud credentials
            try:
                from google.oauth2 import service_account
                credentials_path = self.project_root / "config" / "stormlight-short-03170a60139e.json"
                if credentials_path.exists():
                    print("🔐 Using service account credentials for Gemini API")
                    # Note: Gemini API requires API key, not service account
                    print("⚠️  Warning: Gemini API requires GEMINI_API_KEY environment variable")
                    print("   Get your API key from: https://aistudio.google.com/app/apikey")
                    sys.exit(1)
            except ImportError:
                pass
            
            print("❌ Error: GEMINI_API_KEY environment variable not set")
            print("Get your API key from: https://aistudio.google.com/app/apikey")
            print("Then set it with: export GEMINI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
    
    def generate_video(self, 
                      prompt: str, 
                      scene_name: str = "scene",
                      take_number: int = None,
                      reference_image: Optional[Path] = None,
                      notes: str = "") -> Dict[str, Any]:
        """
        Generate a video using Veo 3 via Gemini API
        
        Args:
            prompt: Text description for video generation
            scene_name: Scene identifier (e.g., 'title_sequence')
            take_number: Take number (auto-incremented if None)
            reference_image: Optional reference image path
            notes: Optional notes about the generation
            
        Returns:
            Dictionary with generation results
        """
        print(f"🎬 Generating video for scene: {scene_name}")
        print(f"📝 Prompt: {prompt}")
        
        # Auto-increment take number if not provided
        if take_number is None:
            take_number = self._get_next_take_number(scene_name)
        
        # Generate timestamp and filename
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{scene_name}_take{take_number:02d}_{timestamp_str}.mp4"
        output_path = self.flow_exports_dir / filename
        
        try:
            # Prepare generation request
            print("🚀 Starting video generation...")
            
            # Create the model
            model = genai.GenerativeModel('veo-3.0-generate-preview')
            
            # Prepare input
            inputs = [prompt]
            if reference_image and reference_image.exists():
                print(f"🖼️  Using reference image: {reference_image}")
                # Upload the image
                image_file = genai.upload_file(reference_image)
                inputs.insert(0, image_file)
            
            # Generate video
            response = model.generate_content(
                inputs,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )
            
            # Poll for completion
            print("⏳ Waiting for video generation to complete...")
            operation = response
            
            # Note: The actual polling mechanism may vary based on Gemini API implementation
            # This is a simplified version - you may need to adjust based on actual API
            
            max_wait_time = 300  # 5 minutes
            wait_time = 0
            poll_interval = 10
            
            while wait_time < max_wait_time:
                try:
                    # Check if generation is complete
                    if hasattr(response, 'video') and response.video:
                        print("✅ Video generation completed!")
                        
                        # Save the video
                        with open(output_path, 'wb') as f:
                            f.write(response.video.data)
                        
                        break
                    elif hasattr(response, 'parts') and response.parts:
                        # Check if any part contains video data
                        for part in response.parts:
                            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('video/'):
                                print("✅ Video generation completed!")
                                with open(output_path, 'wb') as f:
                                    f.write(part.inline_data.data)
                                break
                        else:
                            # No video found yet, continue waiting
                            time.sleep(poll_interval)
                            wait_time += poll_interval
                            print(f"⏳ Still generating... ({wait_time}s elapsed)")
                            continue
                        break
                    else:
                        time.sleep(poll_interval)
                        wait_time += poll_interval
                        print(f"⏳ Still generating... ({wait_time}s elapsed)")
                
                except Exception as e:
                    print(f"⚠️  Polling error: {e}")
                    time.sleep(poll_interval)
                    wait_time += poll_interval
            
            if wait_time >= max_wait_time:
                raise TimeoutError("Video generation timed out after 5 minutes")
            
            # Verify file was created
            if not output_path.exists():
                raise FileNotFoundError("Generated video file not found")
            
            file_size = output_path.stat().st_size
            print(f"💾 Video saved: {filename} ({file_size / 1024 / 1024:.1f} MB)")
            
            # Create ledger entry
            ledger_entry = {
                "timestamp": timestamp.isoformat(),
                "scene": scene_name,
                "take": take_number,
                "prompt": prompt,
                "duration": 8,  # Veo 3 generates 8-second clips
                "resolution": "720p",
                "model": "veo-3.0-generate-preview",
                "quality": "high",
                "filename": filename,
                "file_size_bytes": file_size,
                "reference_image": str(reference_image) if reference_image else None,
                "notes": notes
            }
            
            # Append to ledger
            self._append_to_ledger(ledger_entry)
            
            print(f"📝 Added to ledger: {scene_name} take {take_number}")
            
            return {
                "success": True,
                "output_path": output_path,
                "ledger_entry": ledger_entry,
                "take_number": take_number
            }
            
        except Exception as e:
            print(f"❌ Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "scene": scene_name,
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
    
    def _append_to_ledger(self, entry: Dict[str, Any]):
        """Append entry to the JSONL ledger file"""
        with open(self.ledger_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

def main():
    """Command line interface for Veo 3 generation"""
    parser = argparse.ArgumentParser(description="Generate Veo 3 videos using Gemini API")
    parser.add_argument("prompt", help="Text prompt for video generation")
    parser.add_argument("--scene", default="test_scene", help="Scene name (e.g., title_sequence)")
    parser.add_argument("--take", type=int, help="Take number (auto-incremented if not provided)")
    parser.add_argument("--image", type=Path, help="Optional reference image path")
    parser.add_argument("--notes", default="", help="Optional notes about the generation")
    
    args = parser.parse_args()
    
    # Create generator
    generator = Veo3Generator()
    
    # Generate video
    result = generator.generate_video(
        prompt=args.prompt,
        scene_name=args.scene,
        take_number=args.take,
        reference_image=args.image,
        notes=args.notes
    )
    
    if result["success"]:
        print(f"\n🎉 SUCCESS! Video generated:")
        print(f"📁 File: {result['output_path']}")
        print(f"🎬 Scene: {result['ledger_entry']['scene']}")
        print(f"🎯 Take: {result['take_number']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
