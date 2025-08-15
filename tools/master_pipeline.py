#!/usr/bin/env python3
"""
Master Pipeline Controller - End-to-end automation for Stormlight Short production
Orchestrates the complete workflow from styleframes to final video generation.
"""

import json
import yaml
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from vertex_manager import VertexVideoManager
from flow_manager import FlowManager
from midjourney_manager import MidjourneyManager
from automation_orchestrator import StormLightOrchestrator
from pipeline_monitor import PipelineMonitor


class MasterPipeline:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / "config" / "pipeline_config.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.orchestrator = StormLightOrchestrator(self.project_root, self.config_path)
        self.monitor = PipelineMonitor(self.project_root)
        
        # Pipeline state
        self.pipeline_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.pipeline_log = []
        self.total_cost = 0.0
        
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log pipeline event"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.pipeline_log.append(log_entry)
        print(log_entry)
    
    def save_pipeline_report(self):
        """Save comprehensive pipeline execution report"""
        report_path = self.project_root / "00_docs" / f"pipeline_report_{self.pipeline_id}.json"
        
        report = {
            "pipeline_id": self.pipeline_id,
            "timestamp": datetime.now().isoformat(),
            "total_cost": self.total_cost,
            "configuration": self.config,
            "execution_log": self.pipeline_log,
            "status": "completed"
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Pipeline report saved: {report_path}")
    
    async def process_scene(self, scene_name: str, scene_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complete scene from styleframes to video"""
        self.log(f"Processing scene: {scene_name}")
        results = {
            "scene": scene_name,
            "styleframes": [],
            "prompts": [],
            "vertex_jobs": [],
            "flow_exports": [],
            "status": "started"
        }
        
        try:
            # Step 1: Process Midjourney styleframes
            styleframes_dir = self.project_root / "01_styleframes_midjourney" / scene_name
            if styleframes_dir.exists():
                self.log(f"Processing styleframes for {scene_name}")
                for img_file in styleframes_dir.glob("*.png"):
                    results["styleframes"].append(str(img_file))
            
            # Step 2: Load and process prompt templates
            prompt_template_path = self.project_root / "02_prompts" / f"{scene_name}_template.yaml"
            if prompt_template_path.exists():
                with open(prompt_template_path, 'r') as f:
                    template = yaml.safe_load(f)
                
                base_prompts = template.get("base_prompts", {})
                for prompt_name, prompt_data in base_prompts.items():
                    self.log(f"Processing prompt: {prompt_name}")
                    results["prompts"].append({
                        "name": prompt_name,
                        "prompt": prompt_data["prompt"],
                        "seed": prompt_data.get("seed"),
                        "duration": prompt_data.get("duration", 5)
                    })
            
            # Step 3: Submit Vertex AI jobs for each prompt
            for prompt_info in results["prompts"]:
                self.log(f"Submitting Vertex job: {scene_name}/{prompt_info['name']}")
                
                job_id = self.orchestrator.process_vertex_job(
                    scene_name=scene_name,
                    prompt=prompt_info["prompt"],
                    seed=prompt_info.get("seed"),
                    duration=prompt_info.get("duration", 5),
                    resolution=self.config.get("vertex_ai", {}).get("default_settings", {}).get("resolution", "1280x720"),
                    dry_run=False  # Set to True for testing
                )
                
                if job_id:
                    results["vertex_jobs"].append(job_id)
                    # Track cost
                    job_cost = prompt_info.get("duration", 5) * 0.0375  # Base rate
                    self.total_cost += job_cost
                    self.log(f"Job {job_id} submitted (cost: ${job_cost:.2f})")
                
                # Rate limiting
                await asyncio.sleep(2)
            
            # Step 4: Process Flow exports if available
            flow_exports_dir = self.project_root / "04_flow_exports" / scene_name
            if flow_exports_dir.exists():
                self.log(f"Processing Flow exports for {scene_name}")
                for export_file in flow_exports_dir.glob("*.*"):
                    results["flow_exports"].append(str(export_file))
            
            results["status"] = "completed"
            self.log(f"Scene {scene_name} processing completed")
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            self.log(f"Error processing scene {scene_name}: {e}", "ERROR")
        
        return results
    
    async def run_full_pipeline(self, scenes: List[str] = None):
        """Run the complete pipeline for specified scenes"""
        self.log("Starting full pipeline execution")
        
        # Determine scenes to process
        if not scenes:
            scenes = list(self.config.get("scenes", {}).keys())
        
        self.log(f"Processing {len(scenes)} scenes: {', '.join(scenes)}")
        
        # Process scenes concurrently
        tasks = []
        for scene_name in scenes:
            scene_config = self.config.get("scenes", {}).get(scene_name, {})
            task = asyncio.create_task(self.process_scene(scene_name, scene_config))
            tasks.append(task)
        
        # Wait for all scenes to complete
        results = await asyncio.gather(*tasks)
        
        # Sync to GCS
        self.log("Syncing to Google Cloud Storage")
        self.orchestrator.sync_to_gcs(dry_run=False)
        
        # Generate summary
        self.log("Generating pipeline summary")
        summary = {
            "pipeline_id": self.pipeline_id,
            "scenes_processed": len(results),
            "total_vertex_jobs": sum(len(r["vertex_jobs"]) for r in results),
            "total_cost": self.total_cost,
            "results": results
        }
        
        # Save report
        self.save_pipeline_report()
        
        return summary
    
    def run_batch_generation(self, batch_config_path: Path) -> Dict[str, Any]:
        """Run batch video generation from configuration file"""
        self.log(f"Loading batch configuration: {batch_config_path}")
        
        with open(batch_config_path, 'r') as f:
            batch_config = json.load(f)
        
        results = {
            "batch_id": batch_config.get("batch_id", self.pipeline_id),
            "jobs": []
        }
        
        # Process each job in batch
        for job_config in batch_config.get("jobs", []):
            scene = job_config.get("scene")
            prompt = job_config.get("prompt")
            
            self.log(f"Processing batch job: {scene}")
            
            job_id = self.orchestrator.process_vertex_job(
                scene_name=scene,
                prompt=prompt,
                **job_config.get("parameters", {})
            )
            
            results["jobs"].append({
                "scene": scene,
                "job_id": job_id,
                "status": "submitted" if job_id else "failed"
            })
            
            # Rate limiting
            time.sleep(1)
        
        # Sync to GCS
        self.orchestrator.sync_to_gcs(dry_run=False)
        
        return results
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate pipeline configuration and readiness"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "valid": True,
            "checks": {}
        }
        
        # Check GCP configuration
        if self.config.get("gcp_project_id") == "your-project-id":
            validation_results["checks"]["gcp_config"] = "❌ GCP project ID not configured"
            validation_results["valid"] = False
        else:
            validation_results["checks"]["gcp_config"] = "✅ GCP configured"
        
        # Check scene configurations
        scenes = self.config.get("scenes", {})
        if not scenes:
            validation_results["checks"]["scenes"] = "❌ No scenes configured"
            validation_results["valid"] = False
        else:
            validation_results["checks"]["scenes"] = f"✅ {len(scenes)} scenes configured"
        
        # Check prompt templates
        prompts_dir = self.project_root / "02_prompts"
        templates = list(prompts_dir.glob("*_template.yaml"))
        if not templates:
            validation_results["checks"]["prompts"] = "⚠️ No prompt templates found"
        else:
            validation_results["checks"]["prompts"] = f"✅ {len(templates)} prompt templates"
        
        # Check authentication
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--format=json"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                validation_results["checks"]["auth"] = "✅ GCP authenticated"
            else:
                validation_results["checks"]["auth"] = "❌ GCP not authenticated"
                validation_results["valid"] = False
        except:
            validation_results["checks"]["auth"] = "❌ gcloud not installed"
            validation_results["valid"] = False
        
        return validation_results
    
    async def run_scene_test(self, scene_name: str):
        """Run a test generation for a single scene"""
        self.log(f"Running test for scene: {scene_name}")
        
        # Use dry run mode for testing
        scene_config = self.config.get("scenes", {}).get(scene_name, {})
        
        # Get first prompt from template
        prompt_template_path = self.project_root / "02_prompts" / f"{scene_name}_template.yaml"
        if prompt_template_path.exists():
            with open(prompt_template_path, 'r') as f:
                template = yaml.safe_load(f)
            
            base_prompts = template.get("base_prompts", {})
            if base_prompts:
                first_prompt = list(base_prompts.values())[0]
                
                self.log(f"Test prompt: {first_prompt['prompt'][:100]}...")
                
                # Submit test job (dry run)
                job_id = self.orchestrator.process_vertex_job(
                    scene_name=scene_name,
                    prompt=first_prompt["prompt"],
                    duration=3,  # Short duration for testing
                    resolution="1280x720",
                    dry_run=True  # Dry run mode
                )
                
                if job_id:
                    self.log(f"Test job created: {job_id}")
                    return {"success": True, "job_id": job_id}
        
        return {"success": False, "error": "No prompt template found"}


def main():
    """CLI interface for master pipeline"""
    parser = argparse.ArgumentParser(description="Master Pipeline Controller")
    
    # Commands
    parser.add_argument("--full-pipeline", action="store_true", 
                       help="Run full pipeline for all scenes")
    parser.add_argument("--scenes", nargs="+", 
                       help="Specific scenes to process")
    parser.add_argument("--batch", type=str, 
                       help="Path to batch configuration JSON")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate pipeline configuration")
    parser.add_argument("--test-scene", type=str, 
                       help="Run test generation for a scene")
    parser.add_argument("--monitor", action="store_true", 
                       help="Launch monitoring dashboard")
    
    args = parser.parse_args()
    
    pipeline = MasterPipeline()
    
    if args.validate:
        results = pipeline.validate_pipeline()
        print("\n🔍 Pipeline Validation Results\n")
        for check, result in results["checks"].items():
            print(f"  {check}: {result}")
        
        if results["valid"]:
            print("\n✅ Pipeline is ready to run!")
        else:
            print("\n❌ Pipeline validation failed. Please fix issues above.")
    
    elif args.test_scene:
        asyncio.run(pipeline.run_scene_test(args.test_scene))
    
    elif args.batch:
        batch_path = Path(args.batch)
        if batch_path.exists():
            results = pipeline.run_batch_generation(batch_path)
            print(f"\nBatch processing completed: {len(results['jobs'])} jobs submitted")
        else:
            print(f"Batch config not found: {batch_path}")
    
    elif args.full_pipeline:
        summary = asyncio.run(pipeline.run_full_pipeline(args.scenes))
        print(f"\n✅ Pipeline completed!")
        print(f"  Scenes: {summary['scenes_processed']}")
        print(f"  Jobs: {summary['total_vertex_jobs']}")
        print(f"  Cost: ${summary['total_cost']:.2f}")
    
    elif args.monitor:
        monitor = PipelineMonitor()
        asyncio.run(monitor.run_dashboard())
    
    else:
        # Default: show status
        health = pipeline.monitor.run_health_check()
        print("\n📊 Pipeline Status\n")
        for check, result in health["checks"].items():
            print(f"  {check}: {result}")
        print(f"\nUse --help to see available commands")


if __name__ == "__main__":
    main()