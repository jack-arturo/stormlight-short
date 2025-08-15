#!/usr/bin/env python3
"""
Veo 3 API Test Script for Stormlight Archives
Tests direct access to Google's Veo 3 video generation model
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from google.cloud import aiplatform
from google.oauth2 import service_account
import requests

# Configuration
PROJECT_ID = "stormlight-short"
LOCATION = "us-central1"
SERVICE_ACCOUNT_PATH = "./config/stormlight-short-03170a60139e.json"
OUTPUT_DIR = Path("./media/veo3_tests")

def setup_authentication():
    """Set up Google Cloud authentication using service account"""
    print("🔐 Setting up authentication...")
    
    # Set environment variable for authentication
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = SERVICE_ACCOUNT_PATH
    
    # Load service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    # Initialize Vertex AI
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        credentials=credentials
    )
    
    print(f"✅ Authenticated with project: {PROJECT_ID}")
    print(f"✅ Using location: {LOCATION}")
    return credentials

def create_output_directory():
    """Create output directory for test videos"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory ready: {OUTPUT_DIR}")

def test_stormlight_title_card():
    """Generate Stormlight Into the Tempest title card with Veo 3"""
    
    print("\n🎬 Testing Stormlight Title Card Generation...")
    
    # Stormlight-specific prompt optimized for Veo 3
    prompt = """Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere with floating spren - tiny spirit creatures like ribbons of light dancing through the air. Camera slowly reveals vast alien landscape, then elegant title text fades in: "STORMLIGHT: INTO THE TEMPEST". Cinematic wide shot, Attack on Titan meets Studio Ghibli animation style, epic fantasy film opening sequence."""
    
    negative_prompt = "earth plants, normal vegetation, sunny weather, modern buildings, realistic humans, photorealistic, live action, text overlay during scene"
    
    # Veo 3 request payload
    request_payload = {
        "instances": [{
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "video_config": {
                "duration_seconds": 6,
                "width": 1280,
                "height": 720,
                "aspect_ratio": "16:9",
                "fps": 24
            },
            "generation_config": {
                "temperature": 0.7,
                "guidance_scale": 7.5,
                "seed": 42  # For reproducibility
            }
        }],
        "parameters": {
            "model": "veo-3-preview"
        }
    }
    
    print(f"📝 Prompt: {prompt[:100]}...")
    print(f"⚙️  Config: 6s, 720p, seed=42")
    
    return request_payload

def submit_veo3_job(request_payload):
    """Submit job to Veo 3 via Vertex AI"""
    
    print("\n🚀 Submitting to Veo 3...")
    
    try:
        # Create endpoint for Veo 3
        endpoint_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3-preview"
        
        print(f"🎯 Endpoint: {endpoint_name}")
        
        # Create the prediction request
        endpoint = aiplatform.Endpoint(endpoint_name)
        
        # Submit prediction
        response = endpoint.predict(
            instances=request_payload["instances"],
            parameters=request_payload["parameters"]
        )
        
        print("✅ Job submitted successfully!")
        return response
        
    except Exception as e:
        print(f"❌ Error submitting job: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Try alternative approach with direct API call
        print("\n🔄 Trying alternative API approach...")
        return try_alternative_api(request_payload)

def try_alternative_api(request_payload):
    """Try alternative API approach for Veo 3"""
    
    try:
        # Use the aiplatform prediction service directly
        from google.cloud.aiplatform import gapic
        
        client = gapic.PredictionServiceClient()
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3-preview"
        
        # Convert request to proper format
        instances = [json.dumps(instance) for instance in request_payload["instances"]]
        parameters = json.dumps(request_payload["parameters"])
        
        response = client.predict(
            endpoint=endpoint,
            instances=instances,
            parameters=parameters
        )
        
        print("✅ Alternative API successful!")
        return response
        
    except Exception as e:
        print(f"❌ Alternative API also failed: {e}")
        print("\n💡 This might mean:")
        print("   - Veo 3 is not yet available in your region")
        print("   - Additional permissions needed")
        print("   - Model name has changed")
        print("   - Preview access required")
        
        return None

def save_test_results(request_payload, response=None, error=None):
    """Save test results for analysis"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"veo3_test_{timestamp}.json"
    
    results = {
        "timestamp": timestamp,
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "request_payload": request_payload,
        "success": response is not None,
        "error": str(error) if error else None,
        "response_summary": str(response)[:500] if response else None
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {results_file}")

def main():
    """Main test execution"""
    
    print("🎬 Stormlight Archives - Veo 3 API Test")
    print("=" * 50)
    
    # Setup
    try:
        setup_authentication()
        create_output_directory()
        
        # Create test request
        request_payload = test_stormlight_title_card()
        
        # Submit to Veo 3
        response = submit_veo3_job(request_payload)
        
        # Save results
        save_test_results(request_payload, response)
        
        if response:
            print("\n🎉 SUCCESS! Veo 3 API is working")
            print("📹 Video generation job submitted")
            print(f"📁 Check {OUTPUT_DIR} for results")
        else:
            print("\n⚠️  API test completed with issues")
            print("📋 Check the saved results for debugging info")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        save_test_results({}, error=e)

if __name__ == "__main__":
    main()
