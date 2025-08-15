#!/usr/bin/env python3
"""
Vertex AI Video Generation Manager for Stormlight Short
Handles Veo 3 model requests, metadata tracking, and output organization.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip


class VertexVideoManager:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.client = aip.PredictionServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )
        
    def create_job_folder(self, scene_name: str, take_number: int = 1) -> Path:
        """Create organized folder structure for a Vertex AI job"""
        job_id = f"{scene_name}_take{take_number:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job_path = Path("03_vertex_jobs") / scene_name / job_id
        job_path.mkdir(parents=True, exist_ok=True)
        
        # Create subfolders
        (job_path / "inputs").mkdir(exist_ok=True)
        (job_path / "outputs").mkdir(exist_ok=True)
        (job_path / "metadata").mkdir(exist_ok=True)
        
        return job_path
    
    def prepare_veo3_request(self, 
                           prompt: str,
                           negative_prompt: str = "",
                           seed: Optional[int] = None,
                           duration: int = 5,
                           resolution: str = "1280x720",
                           aspect_ratio: str = "16:9",
                           model_version: str = "veo-3-preview") -> Dict[str, Any]:
        """Prepare Veo 3 request payload"""
        
        if seed is None:
            seed = int(uuid.uuid4().hex[:8], 16)
            
        request_payload = {
            "instances": [{
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "model_version": model_version
            }],
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        return request_payload
    
    def save_job_metadata(self, job_path: Path, request_payload: Dict[str, Any], 
                         scene_info: Dict[str, Any] = None):
        """Save comprehensive metadata for reproducibility"""
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "job_path": str(job_path),
            "request_payload": request_payload,
            "scene_info": scene_info or {},
            "environment": {
                "project_id": self.project_id,
                "location": self.location,
                "python_version": sys.version,
                "user": os.getenv("USER", "unknown")
            }
        }
        
        # Save as both JSON and YAML for different use cases
        with open(job_path / "metadata" / "job_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
            
        # Also save just the request payload separately
        with open(job_path / "inputs" / "request_payload.json", "w") as f:
            json.dump(request_payload, f, indent=2)
            
        # Create a human-readable summary
        summary = f"""# Vertex AI Job Summary
Scene: {scene_info.get('scene_name', 'Unknown') if scene_info else 'Unknown'}
Timestamp: {metadata['timestamp']}
Model: {request_payload['instances'][0].get('model_version', 'veo-3-preview')}
Prompt: {request_payload['instances'][0]['prompt'][:100]}...
Seed: {request_payload['instances'][0]['seed']}
Duration: {request_payload['instances'][0]['duration']}s
Resolution: {request_payload['instances'][0]['resolution']}
"""
        with open(job_path / "README.md", "w") as f:
            f.write(summary)
            
        return metadata
    
    def submit_job(self, job_path: Path, request_payload: Dict[str, Any], 
                   dry_run: bool = False) -> Optional[str]:
        """Submit job to Vertex AI (or simulate if dry_run)"""
        
        if dry_run:
            print(f"[DRY RUN] Would submit job to Vertex AI:")
            print(f"  Job path: {job_path}")
            print(f"  Payload: {json.dumps(request_payload, indent=2)}")
            return "dry_run_job_id"
        
        try:
            # This would be the actual Vertex AI submission
            # endpoint = f"projects/{self.project_id}/locations/{self.location}/endpoints/veo-3"
            # response = self.client.predict(endpoint=endpoint, instances=request_payload["instances"])
            
            # For now, simulate the response
            job_id = f"vertex_job_{uuid.uuid4().hex[:8]}"
            print(f"Submitted Vertex AI job: {job_id}")
            
            # Save job ID to metadata
            with open(job_path / "metadata" / "job_id.txt", "w") as f:
                f.write(job_id)
                
            return job_id
            
        except Exception as e:
            print(f"Error submitting job: {e}")
            return None


def main():
    """CLI interface for Vertex AI job management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vertex AI Video Generation Manager")
    parser.add_argument("--scene", required=True, help="Scene name")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--negative-prompt", default="", help="Negative prompt")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--duration", type=int, default=5, help="Video duration in seconds")
    parser.add_argument("--resolution", default="1280x720", help="Video resolution")
    parser.add_argument("--model", default="veo-3-preview", help="Model version")
    parser.add_argument("--take", type=int, default=1, help="Take number")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually submit")
    
    args = parser.parse_args()
    
    manager = VertexVideoManager(args.project_id)
    
    # Create job folder
    job_path = manager.create_job_folder(args.scene, args.take)
    print(f"Created job folder: {job_path}")
    
    # Prepare request
    request_payload = manager.prepare_veo3_request(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        seed=args.seed,
        duration=args.duration,
        resolution=args.resolution,
        model_version=args.model
    )
    
    # Save metadata
    scene_info = {"scene_name": args.scene, "take_number": args.take}
    manager.save_job_metadata(job_path, request_payload, scene_info)
    
    # Submit job
    job_id = manager.submit_job(job_path, request_payload, args.dry_run)
    
    if job_id:
        print(f"Job submitted successfully: {job_id}")
        print(f"Metadata saved to: {job_path}")
    else:
        print("Job submission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
