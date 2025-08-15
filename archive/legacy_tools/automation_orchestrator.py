#!/usr/bin/env python3
"""
Automation Orchestrator for Stormlight Short
Coordinates all pipeline operations: sync, Vertex AI, Flow, Midjourney, and prompt ledgers.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import yaml

from vertex_manager import VertexVideoManager
from flow_manager import FlowManager
from midjourney_manager import MidjourneyManager


class StormLightOrchestrator:
    def __init__(self, project_root: Path = None, config_path: Path = None):
        self.project_root = project_root or Path.cwd()
        self.config_path = config_path or (self.project_root / "config" / "pipeline_config.yaml")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize managers
        self.vertex_manager = VertexVideoManager(
            project_id=self.config.get("gcp_project_id", ""),
            location=self.config.get("gcp_location", "us-central1")
        )
        self.flow_manager = FlowManager(self.project_root)
        self.midjourney_manager = MidjourneyManager(self.project_root)
        
        # Paths
        self.sync_script = self.project_root / "tools" / "sync_to_gcs.py.py"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Create default config
            default_config = {
                "gcp_project_id": "your-project-id",
                "gcp_location": "us-central1",
                "gcs_bucket": "stormlight-short",
                "sync_settings": {
                    "auto_sync": True,
                    "dry_run_first": True,
                    "exclude_patterns": ["*.tmp", "*.DS_Store", "*.crdownload"]
                },
                "scenes": {
                    "opening": {
                        "description": "Opening sequence with Kaladin",
                        "style_descriptors": ["windswept", "dramatic", "stormy"]
                    },
                    "bridge_run": {
                        "description": "Bridge crew running scene",
                        "style_descriptors": ["action", "desperate", "chaotic"]
                    }
                }
            }
            
            # Create config directory and save default
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            print(f"Created default config at {self.config_path}")
            print("Please update with your GCP project details")
            
            return default_config
    
    def sync_to_gcs(self, dry_run: bool = None, delete: bool = False) -> bool:
        """Execute sync to GCS with logging"""
        if dry_run is None:
            dry_run = self.config.get("sync_settings", {}).get("dry_run_first", True)
        
        bucket = self.config.get("gcs_bucket", "stormlight-short")
        
        cmd = [
            "python3", str(self.sync_script),
            "--local", str(self.project_root),
            "--bucket", bucket,
            "--logdir", "00_docs/sync_logs"
        ]
        
        if dry_run:
            cmd.append("--dry-run")
        if delete:
            cmd.append("--delete")
        
        # Add exclude patterns
        exclude_patterns = self.config.get("sync_settings", {}).get("exclude_patterns", [])
        for pattern in exclude_patterns:
            cmd.extend(["--exclude", pattern])
        
        print(f"Running sync command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("Sync completed successfully")
                print(result.stdout)
                return True
            else:
                print(f"Sync failed with return code {result.returncode}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error running sync: {e}")
            return False
    
    def process_vertex_job(self, scene_name: str, prompt: str, 
                          take_number: int = 1, **kwargs) -> Optional[str]:
        """Process a Vertex AI video generation job"""
        
        print(f"Processing Vertex AI job for scene '{scene_name}', take {take_number}")
        
        # Create job folder
        job_path = self.vertex_manager.create_job_folder(scene_name, take_number)
        
        # Prepare request
        request_payload = self.vertex_manager.prepare_veo3_request(
            prompt=prompt,
            negative_prompt=kwargs.get("negative_prompt", ""),
            seed=kwargs.get("seed"),
            duration=kwargs.get("duration", 5),
            resolution=kwargs.get("resolution", "1280x720"),
            model_version=kwargs.get("model_version", "veo-3-preview")
        )
        
        # Save metadata
        scene_info = {"scene_name": scene_name, "take_number": take_number}
        self.vertex_manager.save_job_metadata(job_path, request_payload, scene_info)
        
        # Submit job
        job_id = self.vertex_manager.submit_job(
            job_path, request_payload, 
            dry_run=kwargs.get("dry_run", False)
        )
        
        if job_id and self.config.get("sync_settings", {}).get("auto_sync", True):
            print("Auto-syncing after Vertex AI job creation...")
            self.sync_to_gcs(dry_run=True)  # Always dry run first for safety
        
        return job_id
    
    def process_flow_exports(self, source_dir: Path, scene_mapping: Dict[str, Dict]) -> List[Path]:
        """Process Flow exports with automatic organization"""
        
        print(f"Processing Flow exports from {source_dir}")
        
        organized_files = self.flow_manager.batch_organize_exports(source_dir, scene_mapping)
        
        if organized_files and self.config.get("sync_settings", {}).get("auto_sync", True):
            print("Auto-syncing after Flow export processing...")
            self.sync_to_gcs(dry_run=True)
        
        return organized_files
    
    def process_midjourney_styleframes(self, source_dir: Path, 
                                     scene_mapping: Dict[str, Dict]) -> List[Path]:
        """Process Midjourney style frames with validation and organization"""
        
        print(f"Processing Midjourney style frames from {source_dir}")
        
        organized_files = self.midjourney_manager.batch_organize_styleframes(source_dir, scene_mapping)
        
        if organized_files and self.config.get("sync_settings", {}).get("auto_sync", True):
            print("Auto-syncing after Midjourney processing...")
            self.sync_to_gcs(dry_run=True)
        
        return organized_files
    
    def generate_prompt_ledger_summary(self) -> Dict[str, Any]:
        """Generate comprehensive prompt ledger summary"""
        
        prompts_dir = self.project_root / "02_prompts"
        summary = {
            "generated_at": datetime.now().isoformat(),
            "scenes": {},
            "total_entries": 0
        }
        
        # Process all ledger files
        for ledger_file in prompts_dir.glob("*_ledger.json"):
            try:
                with open(ledger_file, 'r') as f:
                    ledger_data = json.load(f)
                
                scene_name = ledger_data.get("scene_name", "unknown")
                ledger_type = ledger_data.get("type", "general")
                
                if scene_name not in summary["scenes"]:
                    summary["scenes"][scene_name] = {}
                
                summary["scenes"][scene_name][ledger_type] = {
                    "entries_count": len(ledger_data.get("entries", [])),
                    "last_updated": ledger_data.get("updated", "unknown"),
                    "file_path": str(ledger_file)
                }
                
                summary["total_entries"] += len(ledger_data.get("entries", []))
                
            except Exception as e:
                print(f"Error processing ledger {ledger_file}: {e}")
        
        # Save summary
        summary_path = prompts_dir / "ledger_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Generated prompt ledger summary: {summary_path}")
        return summary
    
    def setup_automation_schedule(self, schedule_type: str = "launchd") -> bool:
        """Set up automated scheduling for sync operations"""
        
        if schedule_type == "launchd" and sys.platform == "darwin":
            return self._setup_launchd_schedule()
        elif schedule_type == "cron":
            return self._setup_cron_schedule()
        else:
            print(f"Unsupported schedule type: {schedule_type}")
            return False
    
    def _setup_launchd_schedule(self) -> bool:
        """Set up launchd plist for macOS automation"""
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stormlight.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{self.project_root}/tools/automation_orchestrator.py</string>
        <string>--sync-only</string>
        <string>--auto</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.project_root}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>{self.project_root}/00_docs/sync_logs/launchd_sync.log</string>
    <key>StandardErrorPath</key>
    <string>{self.project_root}/00_docs/sync_logs/launchd_sync_error.log</string>
</dict>
</plist>"""
        
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.stormlight.sync.plist"
        
        try:
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load the plist
            subprocess.run(["launchctl", "load", str(plist_path)], check=True)
            print(f"Created and loaded launchd schedule: {plist_path}")
            return True
            
        except Exception as e:
            print(f"Error setting up launchd schedule: {e}")
            return False
    
    def _setup_cron_schedule(self) -> bool:
        """Set up cron job for automation"""
        
        cron_entry = f"0 * * * * cd {self.project_root} && python3 tools/automation_orchestrator.py --sync-only --auto >> 00_docs/sync_logs/cron_sync.log 2>&1"
        
        print(f"Add this line to your crontab (crontab -e):")
        print(cron_entry)
        print("This will sync every hour")
        
        return True


def main():
    """CLI interface for automation orchestrator"""
    
    parser = argparse.ArgumentParser(description="Stormlight Short Automation Orchestrator")
    parser.add_argument("--config", help="Path to configuration file")
    
    # Operations
    parser.add_argument("--sync-only", action="store_true", help="Only perform sync operation")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--delete", action="store_true", help="Delete remote files not present locally")
    parser.add_argument("--auto", action="store_true", help="Automated mode (less verbose)")
    
    # Vertex AI
    parser.add_argument("--vertex-job", help="Create Vertex AI job for scene")
    parser.add_argument("--prompt", help="Prompt for Vertex AI job")
    parser.add_argument("--take", type=int, default=1, help="Take number")
    
    # Processing
    parser.add_argument("--process-flow", help="Process Flow exports from directory")
    parser.add_argument("--process-midjourney", help="Process Midjourney exports from directory")
    
    # Utilities
    parser.add_argument("--generate-summary", action="store_true", help="Generate prompt ledger summary")
    parser.add_argument("--setup-schedule", choices=["launchd", "cron"], help="Set up automation schedule")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    config_path = Path(args.config) if args.config else None
    orchestrator = StormLightOrchestrator(config_path=config_path)
    
    if args.sync_only:
        success = orchestrator.sync_to_gcs(dry_run=args.dry_run, delete=args.delete)
        sys.exit(0 if success else 1)
    
    if args.vertex_job and args.prompt:
        job_id = orchestrator.process_vertex_job(
            args.vertex_job, args.prompt, 
            take_number=args.take, dry_run=args.dry_run
        )
        if job_id:
            print(f"Created Vertex AI job: {job_id}")
        else:
            sys.exit(1)
    
    if args.process_flow:
        source_dir = Path(args.process_flow)
        # Would need scene mapping from config
        scene_mapping = orchestrator.config.get("scenes", {})
        organized_files = orchestrator.process_flow_exports(source_dir, scene_mapping)
        print(f"Organized {len(organized_files)} Flow exports")
    
    if args.process_midjourney:
        source_dir = Path(args.process_midjourney)
        scene_mapping = orchestrator.config.get("scenes", {})
        organized_files = orchestrator.process_midjourney_styleframes(source_dir, scene_mapping)
        print(f"Organized {len(organized_files)} Midjourney style frames")
    
    if args.generate_summary:
        summary = orchestrator.generate_prompt_ledger_summary()
        print(f"Generated summary with {summary['total_entries']} total entries")
    
    if args.setup_schedule:
        success = orchestrator.setup_automation_schedule(args.setup_schedule)
        if success:
            print(f"Set up {args.setup_schedule} automation schedule")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
