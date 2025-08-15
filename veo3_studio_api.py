#!/usr/bin/env python3
"""
Veo 3 Test using the exact API calls that Vertex AI Studio makes
This reverse-engineers the web interface calls
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Configuration
PROJECT_ID = "stormlight-short"
LOCATION = "us-central1"
SERVICE_ACCOUNT_PATH = "./config/stormlight-short-03170a60139e.json"
OUTPUT_DIR = Path("./media/veo3_tests")

def get_access_token():
    """Get access token for API calls"""
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    
    # Refresh the token
    credentials.refresh(Request())
    return credentials.token

def test_veo3_direct_api():
    """Test Veo 3 using direct API calls like Vertex AI Studio"""
    
    print("🎬 Testing Veo 3 with direct API calls...")
    
    try:
        # Get access token
        access_token = get_access_token()
        print("✅ Got access token")
        
        # Stormlight prompt
        prompt = """Epic fantasy title sequence: Sweeping aerial cinematography over the alien world of Roshar. Strange crystalline rock formations jutting from barren ground, no grass only glowing alien moss and crystal plants. Stormy dark clouds gathering overhead with supernatural blue-violet lightning. Otherworldly atmosphere, epic fantasy film opening sequence."""
        
        # Try different API endpoints that Vertex AI Studio might use
        endpoints = [
            # Standard Vertex AI prediction endpoint
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3:predict",
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3-preview:predict",
            
            # Alternative endpoints
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/models/veo-3:predict",
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/veo-3:predict",
            
            # Vertex AI Studio specific endpoints
            f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-3:predict",
            f"https://generativelanguage.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/models/veo-3:generateVideo",
        ]
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Goog-User-Project': PROJECT_ID
        }
        
        # Try different request formats
        request_formats = [
            # Format 1: Standard Vertex AI format
            {
                "instances": [{
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, watermark",
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
                }],
                "parameters": {"model": "veo-3"}
            },
            
            # Format 2: Simplified format
            {
                "instances": [{
                    "prompt": prompt,
                    "aspectRatio": "16:9",
                    "duration": "6s"
                }]
            },
            
            # Format 3: Studio-style format
            {
                "prompt": prompt,
                "aspectRatio": "16:9",
                "duration": 6,
                "negativePrompt": "blurry, low quality"
            }
        ]
        
        for i, endpoint in enumerate(endpoints):
            print(f"\n🎯 Trying endpoint {i+1}/{len(endpoints)}: {endpoint.split('/')[-2]}:{endpoint.split('/')[-1]}")
            
            for j, request_data in enumerate(request_formats):
                print(f"   📋 Format {j+1}/{len(request_formats)}")
                
                try:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=request_data,
                        timeout=30
                    )
                    
                    print(f"   📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ SUCCESS! Veo 3 responded!")
                        
                        # Save successful response
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        result_file = OUTPUT_DIR / f"veo3_success_{timestamp}.json"
                        
                        result_data = {
                            "timestamp": timestamp,
                            "endpoint": endpoint,
                            "request_data": request_data,
                            "response_status": response.status_code,
                            "response_data": response.json() if response.content else None
                        }
                        
                        with open(result_file, 'w') as f:
                            json.dump(result_data, f, indent=2)
                        
                        print(f"   💾 Response saved to: {result_file}")
                        
                        # Check if we got a video URL
                        response_json = response.json()
                        if 'predictions' in response_json:
                            for prediction in response_json['predictions']:
                                if 'video_uri' in prediction:
                                    print(f"   🎬 Video URI: {prediction['video_uri']}")
                                elif 'uri' in prediction:
                                    print(f"   🎬 URI: {prediction['uri']}")
                        
                        return response_json
                        
                    elif response.status_code == 400:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                            print(f"   ❌ Bad Request: {error_msg[:100]}...")
                        except:
                            print(f"   ❌ Bad Request: {response.text[:100]}...")
                    
                    elif response.status_code == 404:
                        print("   ❌ Not Found - endpoint doesn't exist")
                    
                    elif response.status_code == 403:
                        print("   ❌ Forbidden - permission denied")
                    
                    else:
                        print(f"   ❌ Error {response.status_code}: {response.text[:100]}...")
                
                except requests.exceptions.Timeout:
                    print("   ⏰ Request timed out")
                except requests.exceptions.RequestException as e:
                    print(f"   💥 Request failed: {str(e)[:100]}...")
                except Exception as e:
                    print(f"   💥 Unexpected error: {str(e)[:100]}...")
        
        print("\n❌ All API attempts failed")
        return None
        
    except Exception as e:
        print(f"💥 API test failed: {e}")
        return None

def check_vertex_ai_studio_models():
    """Check what models are available in Vertex AI Studio"""
    
    print("\n🔍 Checking Vertex AI Studio models...")
    
    try:
        access_token = get_access_token()
        
        # Try to list available models
        list_endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/models"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(list_endpoint, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models.get('models', []))} models")
            
            for model in models.get('models', []):
                display_name = model.get('displayName', '')
                if 'video' in display_name.lower() or 'veo' in display_name.lower():
                    print(f"   🎬 Video model: {display_name}")
        else:
            print(f"❌ Failed to list models: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Model check failed: {e}")

def main():
    """Main execution"""
    
    print("🎬 Stormlight Archives - Direct Veo 3 API Test")
    print("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test direct API access
    result = test_veo3_direct_api()
    
    if not result:
        print("\n🔍 Checking available models...")
        check_vertex_ai_studio_models()
    
    print("\n📋 Manual verification steps:")
    print("1. Go to: https://console.cloud.google.com/vertex-ai/generative")
    print("2. Check if 'Video generation' appears in the left sidebar")
    print("3. If available, try generating a test video manually")
    print("4. Use browser dev tools to see the actual API calls")

if __name__ == "__main__":
    main()
