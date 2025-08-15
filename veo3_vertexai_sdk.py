#!/usr/bin/env python3
"""
Veo 3 Test using the newer Vertex AI SDK approach
This uses the vertexai library which is the recommended way
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Set up authentication first
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./config/stormlight-short-03170a60139e.json"

try:
    import vertexai
    from vertexai.preview.vision_models import VideoGenerationModel
    print("✅ Vertex AI SDK imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing vertexai library...")
    import subprocess
    subprocess.run(["pip", "install", "google-cloud-aiplatform[preview]", "--upgrade"])
    import vertexai
    from vertexai.preview.vision_models import VideoGenerationModel

# Configuration
PROJECT_ID = "stormlight-short"
LOCATION = "us-central1"
OUTPUT_DIR = Path("./media/veo3_tests")

def test_veo3_with_sdk():
    """Test Veo 3 using the official Vertex AI SDK"""
    
    print("🎬 Testing Veo 3 with Vertex AI SDK...")
    
    try:
        # Initialize Vertex AI
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print(f"✅ Vertex AI initialized for project: {PROJECT_ID}")
        
        # Try to load the video generation model
        print("📦 Loading video generation model...")
        
        # Try different model names that might work
        model_names = [
            "veo-3",
            "veo-3-preview", 
            "video-generation@001",
            "imagen-video@001"
        ]
        
        for model_name in model_names:
            try:
                print(f"🎯 Trying model: {model_name}")
                model = VideoGenerationModel.from_pretrained(model_name)
                print(f"✅ Successfully loaded model: {model_name}")
                
                # Generate video with Stormlight prompt
                prompt = """Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere, epic fantasy film opening sequence."""
                
                print("🎬 Generating video...")
                print(f"📝 Prompt: {prompt[:100]}...")
                
                response = model.generate_video(
                    prompt=prompt,
                    negative_prompt="blurry, low quality, distorted, watermark",
                    # Add video-specific parameters if supported
                )
                
                print("✅ Video generation successful!")
                
                # Save the result
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if hasattr(response, 'video_uri'):
                    print(f"📹 Video URI: {response.video_uri}")
                elif hasattr(response, 'images') and response.images:
                    # Some models return images instead of video
                    output_path = OUTPUT_DIR / f"veo3_output_{timestamp}.png"
                    response.images[0].save(output_path)
                    print(f"🖼️  Image saved to: {output_path}")
                
                # Save metadata
                metadata = {
                    "timestamp": timestamp,
                    "model_name": model_name,
                    "prompt": prompt,
                    "success": True,
                    "response_type": str(type(response))
                }
                
                metadata_path = OUTPUT_DIR / f"veo3_metadata_{timestamp}.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"💾 Metadata saved to: {metadata_path}")
                return response
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Model {model_name} failed: {error_msg[:100]}...")
                
                if "not found" in error_msg.lower():
                    print("   → Model not found")
                elif "permission" in error_msg.lower():
                    print("   → Permission denied")
                elif "quota" in error_msg.lower():
                    print("   → Quota exceeded")
                else:
                    print(f"   → Error type: {type(e).__name__}")
                
                continue
        
        print("❌ No video generation models worked")
        return None
        
    except Exception as e:
        print(f"💥 SDK test failed: {e}")
        return None

def check_available_models():
    """Check what models are actually available"""
    
    print("\n🔍 Checking available models...")
    
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Try to list available models
        from vertexai.preview import vision_models
        
        print("📋 Available vision model classes:")
        for attr in dir(vision_models):
            if 'Model' in attr and not attr.startswith('_'):
                print(f"   - {attr}")
        
        # Try to get model info
        try:
            from vertexai.preview.vision_models import ImageGenerationModel
            print("\n✅ ImageGenerationModel is available")
            
            # Test image generation as a fallback
            print("🖼️  Testing image generation as fallback...")
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")
            
            response = model.generate_images(
                prompt="Epic fantasy aerial view of alien crystalline landscape with stormy skies, Stormlight Archives style",
                number_of_images=1,
                aspect_ratio="16:9"
            )
            
            if response.images:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = OUTPUT_DIR / f"stormlight_image_{timestamp}.png"
                response.images[0].save(output_path)
                print(f"✅ Image generated successfully: {output_path}")
                return True
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
        
    except Exception as e:
        print(f"❌ Model check failed: {e}")
    
    return False

def main():
    """Main execution"""
    
    print("🎬 Stormlight Archives - Vertex AI SDK Test")
    print("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test video generation
    result = test_veo3_with_sdk()
    
    if not result:
        print("\n🔄 Video generation failed, checking alternatives...")
        check_available_models()
    
    print("\n📋 Next steps:")
    print("1. Check Vertex AI Studio web interface for available models")
    print("2. Verify Veo 3 access in your Google Cloud console")
    print("3. Consider using image generation + external video tools")

if __name__ == "__main__":
    main()
