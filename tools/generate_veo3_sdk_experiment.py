#!/usr/bin/env python3
"""
🧪 SDK Experiment: Google Gen AI SDK for Veo 3
Test implementation using the official SDK alongside working REST API
"""

import os
import time
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Import the working generator
from generate_veo3 import Veo3Generator

# Google Gen AI SDK
try:
    import google.genai as genai
    from google.genai import types
    GENAI_SDK_AVAILABLE = True
    print("✅ Google Gen AI SDK available")
except ImportError:
    GENAI_SDK_AVAILABLE = False
    print("❌ Google Gen AI SDK not available")
    sys.exit(1)

class Veo3SDKExperiment:
    def __init__(self):
        self.project_root = Path.cwd()
        
        # Set up API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("❌ Error: GEMINI_API_KEY environment variable not set")
            sys.exit(1)
        
        # Check for Vertex AI setup
        use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').lower() == 'true'
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        if use_vertexai and project_id:
            self.client = genai.Client(vertexai=True, project=project_id, location=location)
            self.use_vertexai = True
            print(f"🚀 Using Vertex AI: {project_id} in {location}")
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.use_vertexai = False
            print("🚀 Using Gemini API")
    
    def test_simple_generation(self, prompt: str):
        """Test simple SDK generation following official docs"""
        print(f"\n🧪 Testing SDK with prompt: {prompt}")
        
        try:
            # Use -preview model as requested
            model_name = "veo-3.0-generate-preview"
            print(f"🎬 Model: {model_name}")
            
            # Minimal generation following official docs pattern
            print("⏳ Starting generation...")
            operation = self.client.models.generate_videos(
                model=model_name,
                prompt=prompt,
            )
            
            print(f"🔄 Operation: {operation.name}")
            
            # Wait for completion
            while not operation.done:
                time.sleep(15)
                operation = self.client.operations.get(operation)
                print("⏳ Still generating...")
            
            print("✅ Generation completed!")
            print(f"📊 Response structure: {type(operation.response)}")
            
            if operation.response:
                print(f"📊 Result structure: {type(operation.result)}")
                if hasattr(operation.result, 'generated_videos'):
                    videos = operation.result.generated_videos
                    print(f"📊 Generated videos: {len(videos)}")
                    
                    if videos:
                        video = videos[0]
                        print(f"📊 Video object: {type(video)}")
                        print(f"📊 Video.video: {type(video.video)}")
                        
                        # Check available download methods
                        if hasattr(video.video, 'video_bytes'):
                            print("✅ video_bytes available")
                        if hasattr(video.video, 'uri'):
                            print(f"✅ URI available: {video.video.uri}")
                        
                        return {
                            "success": True,
                            "operation": operation,
                            "video": video
                        }
                else:
                    print("❌ No generated_videos in result")
            else:
                print("❌ No response in operation")
                
            return {"success": False, "error": "No video in response"}
            
        except Exception as e:
            print(f"❌ SDK test failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="🧪 Test Google Gen AI SDK for Veo 3")
    parser.add_argument("prompt", help="Test prompt")
    parser.add_argument("--compare-rest", action="store_true", 
                       help="Also test with working REST API for comparison")
    
    args = parser.parse_args()
    
    # Test SDK
    print("🧪 TESTING GOOGLE GEN AI SDK")
    print("=" * 50)
    
    sdk_test = Veo3SDKExperiment()
    sdk_result = sdk_test.test_simple_generation(args.prompt)
    
    if args.compare_rest:
        print("\n🔄 TESTING WORKING REST API FOR COMPARISON")
        print("=" * 50)
        
        rest_generator = Veo3Generator()
        rest_result = rest_generator.generate_video(
            prompt=args.prompt,
            scene_name="sdk_comparison_rest"
        )
        
        print(f"\n📊 COMPARISON:")
        print(f"SDK Success: {sdk_result['success']}")
        print(f"REST Success: {rest_result['success']}")

if __name__ == "__main__":
    main()
