#!/usr/bin/env python3
"""
WORKING Gemini API Veo 3 Video Generation for Stormlight Archives
Uses the correct REST API format with instances array
"""

import os
import time
import json
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import base64

class Veo3Generator:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.flow_exports_dir = self.project_root / "04_flow_exports"
        self.prompts_dir = self.project_root / "02_prompts"
        self.ledger_file = self.prompts_dir / "ledger.jsonl"
        
        # Ensure directories exist
        self.flow_exports_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Set up API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("❌ Error: GEMINI_API_KEY environment variable not set")
            print("Get your API key from: https://aistudio.google.com/app/apikey")
            print("Then set it with: export GEMINI_API_KEY='your-api-key-here'")
            sys.exit(1)
        
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        print("✅ Gemini API configured successfully")
    
    def generate_video(self, 
                      prompt: str, 
                      scene_name: str = "scene",
                      take_number: int = None,
                      reference_image: Optional[Path] = None,
                      notes: str = "") -> Dict[str, Any]:
        """
        Generate a video using Veo 3 via Gemini REST API
        
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
            print("🚀 Starting video generation...")
            
            # Prepare the payload
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ]
            }
            
            # Add reference image if provided
            if reference_image and reference_image.exists():
                print(f"🖼️  Using reference image: {reference_image}")
                # Read and encode the image
                with open(reference_image, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
                payload["instances"][0]["image"] = {
                    "bytesBase64Encoded": img_data
                }
            
            # Start the generation
            url = "https://generativelanguage.googleapis.com/v1beta/models/veo-3.0-generate-preview:predictLongRunning"
            
            print("⏳ Submitting generation request...")
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            result = response.json()
            operation_name = result.get("name")
            
            if not operation_name:
                raise Exception("No operation name returned from API")
            
            print(f"🔄 Operation started: {operation_name}")
            
            # Poll for completion
            video_data = self._poll_operation(operation_name)
            
            # Save the video
            with open(output_path, 'wb') as f:
                f.write(video_data)
            
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
                "notes": notes,
                "operation_name": operation_name
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
    
    def _poll_operation(self, operation_name: str) -> bytes:
        """Poll the long-running operation until completion"""
        operation_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}"
        
        max_wait_time = 600  # 10 minutes
        wait_time = 0
        poll_interval = 15  # Check every 15 seconds
        
        print("⏳ Polling for completion...")
        
        while wait_time < max_wait_time:
            try:
                response = requests.get(operation_url, headers=self.headers)
                
                if response.status_code != 200:
                    raise Exception(f"Polling failed: {response.status_code} - {response.text}")
                
                operation_result = response.json()
                
                if operation_result.get("done", False):
                    print("✅ Video generation completed!")
                    
                    # Extract the video data
                    if "response" in operation_result:
                        response_data = operation_result["response"]
                        
                        # Check for the new generateVideoResponse format
                        if "generateVideoResponse" in response_data:
                            video_response = response_data["generateVideoResponse"]
                            if "generatedSamples" in video_response:
                                samples = video_response["generatedSamples"]
                                if samples and len(samples) > 0:
                                    sample = samples[0]
                                    if "video" in sample and "uri" in sample["video"]:
                                        video_uri = sample["video"]["uri"]
                                        print(f"📥 Downloading video from: {video_uri}")
                                        return self._download_video(video_uri)
                        
                        # Fallback: Look for older prediction format
                        elif "predictions" in response_data:
                            predictions = response_data["predictions"]
                            if predictions and len(predictions) > 0:
                                prediction = predictions[0]
                                
                                # Look for base64 encoded video data
                                if "bytesBase64Encoded" in prediction:
                                    video_b64 = prediction["bytesBase64Encoded"]
                                    return base64.b64decode(video_b64)
                                elif "videoData" in prediction:
                                    video_b64 = prediction["videoData"]
                                    return base64.b64decode(video_b64)
                    
                    # If we get here, the operation completed but we couldn't find video data
                    print(f"⚠️  Operation completed but no video data found")
                    print(f"Response structure: {json.dumps(operation_result, indent=2)}")
                    raise Exception("Video generation completed but no video data found in response")
                
                else:
                    # Still processing
                    time.sleep(poll_interval)
                    wait_time += poll_interval
                    print(f"⏳ Still generating... ({wait_time}s elapsed)")
                
            except Exception as e:
                if "Video generation completed but no video data found" in str(e):
                    raise  # Re-raise this specific error
                print(f"⚠️  Polling error: {e}")
                time.sleep(poll_interval)
                wait_time += poll_interval
        
        raise TimeoutError("Video generation timed out after 10 minutes")
    
    def _download_video(self, video_uri: str) -> bytes:
        """Download video from the provided URI"""
        try:
            # The URI should be downloadable with the same API key
            response = requests.get(video_uri, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Video download failed: {response.status_code} - {response.text}")
            
            return response.content
            
        except Exception as e:
            raise Exception(f"Failed to download video: {e}")
    
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
