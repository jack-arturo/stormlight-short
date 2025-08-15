#!/usr/bin/env python3
"""
Fixed Veo 3 API Test - Using proper Vertex AI Prediction Service
Based on the latest Google Cloud Vertex AI video generation patterns
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from google.cloud import aiplatform
from google.oauth2 import service_account
from google.cloud.aiplatform import gapic

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

def test_veo3_with_prediction_service():
    """Test Veo 3 using the Prediction Service Client"""
    
    print("\n🎬 Testing Veo 3 with Prediction Service...")
    
    try:
        # Create prediction service client
        client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
        client = gapic.PredictionServiceClient(client_options=client_options)
        
        # Stormlight prompt
        prompt = """Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere with floating spren - tiny spirit creatures like ribbons of light dancing through the air. Camera slowly reveals vast alien landscape. Cinematic wide shot, Attack on Titan meets Studio Ghibli animation style, epic fantasy film opening sequence."""
        
        # Try different endpoint formats for Veo 3
        veo3_endpoints = [
            f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3",
            f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3-preview",
            f"projects/{PROJECT_ID}/locations/{LOCATION}/models/veo-3",
            f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/veo-3"
        ]
        
        for endpoint in veo3_endpoints:
            print(f"\n🎯 Trying endpoint: {endpoint}")
            
            try:
                # Prepare request in the format expected by Vertex AI
                instance = {
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, watermark, text overlay",
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
                        "seed": 42
                    }
                }
                
                # Convert to the format expected by the API
                instances = [json.dumps(instance)]
                parameters = json.dumps({"model": "veo-3"})
                
                print("📤 Submitting request...")
                response = client.predict(
                    endpoint=endpoint,
                    instances=instances,
                    parameters=parameters
                )
                
                print("✅ SUCCESS! Veo 3 responded!")
                print(f"📋 Response type: {type(response)}")
                
                # Save the response
                save_successful_response(response, endpoint, instance)
                return response
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Failed: {error_msg[:100]}...")
                
                # Check for specific error types
                if "not found" in error_msg.lower():
                    print("   → Endpoint not found, trying next...")
                elif "permission" in error_msg.lower():
                    print("   → Permission issue - check IAM roles")
                elif "quota" in error_msg.lower():
                    print("   → Quota exceeded")
                elif "not enabled" in error_msg.lower():
                    print("   → API not enabled")
                else:
                    print(f"   → Unknown error: {type(e).__name__}")
                
                continue
        
        print("\n❌ All endpoints failed. Trying alternative approaches...")
        return try_vertex_ai_studio_approach()
        
    except Exception as e:
        print(f"💥 Prediction service setup failed: {e}")
        return None

def try_vertex_ai_studio_approach():
    """Try using Vertex AI Studio approach"""
    
    print("\n🔄 Trying Vertex AI Studio approach...")
    
    try:
        # This mimics what Vertex AI Studio does
        from google.cloud.aiplatform_v1 import PredictionServiceClient
        from google.cloud.aiplatform_v1.types import PredictRequest
        
        client = PredictionServiceClient()
        
        # Studio-style endpoint
        endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3"
        
        # Studio-style request
        request_data = {
            "prompt": "Epic fantasy aerial view of alien crystalline landscape with stormy skies",
            "aspectRatio": "16:9",
            "duration": "6s"
        }
        
        instances = [request_data]
        
        request = PredictRequest(
            endpoint=endpoint,
            instances=[{"struct_value": {"fields": {k: {"string_value": str(v)} for k, v in request_data.items()}}}]
        )
        
        print("📤 Submitting Studio-style request...")
        response = client.predict(request=request)
        
        print("✅ Studio approach worked!")
        return response
        
    except Exception as e:
        print(f"❌ Studio approach failed: {e}")
        return None

def save_successful_response(response, endpoint, request_data):
    """Save successful response for analysis"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = OUTPUT_DIR / f"veo3_success_{timestamp}.json"
    
    results = {
        "timestamp": timestamp,
        "success": True,
        "endpoint": endpoint,
        "request_data": request_data,
        "response_summary": str(response)[:1000],
        "response_type": str(type(response))
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Success data saved to: {results_file}")

def check_vertex_ai_studio_access():
    """Check if Vertex AI Studio has video generation enabled"""
    
    print("\n🔍 Checking Vertex AI Studio access...")
    print("📋 Manual steps to verify Veo 3 access:")
    print("   1. Go to: https://console.cloud.google.com/vertex-ai/generative")
    print("   2. Look for 'Video generation' or 'Veo' in the left sidebar")
    print("   3. If available, try generating a test video there first")
    print("   4. Check the network tab to see the actual API calls being made")
    
    print("\n🔑 Required permissions for Veo 3:")
    print("   - Vertex AI User (roles/aiplatform.user)")
    print("   - Vertex AI Service Agent (roles/aiplatform.serviceAgent)")
    print("   - Storage Admin (for output files)")
    
    print("\n⚠️  If Veo 3 still doesn't work:")
    print("   - You may need to request access through Google Cloud support")
    print("   - Veo 3 might still be in limited preview")
    print("   - Try using Imagen Video as an alternative")

def main():
    """Main test execution"""
    
    print("🎬 Stormlight Archives - Fixed Veo 3 API Test")
    print("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Setup authentication
        credentials = setup_authentication()
        
        # Test Veo 3 access
        response = test_veo3_with_prediction_service()
        
        if response:
            print("\n🎉 SUCCESS! Veo 3 is working!")
            print("📹 Video generation job submitted")
            print(f"📁 Check {OUTPUT_DIR} for results")
        else:
            print("\n⚠️  Veo 3 API test failed")
            check_vertex_ai_studio_access()
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")

if __name__ == "__main__":
    main()
