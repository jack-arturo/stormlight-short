#!/usr/bin/env python3
"""
Pipeline Monitor - Real-time monitoring dashboard for Stormlight Short production
Tracks Vertex AI jobs, asset processing, and pipeline health.
"""

import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import aiofiles
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
import yaml

console = Console()

class PipelineMonitor:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.config_path = self.project_root / "config" / "pipeline_config.yaml"
        self.vertex_jobs_dir = self.project_root / "03_vertex_jobs"
        self.logs_dir = self.project_root / "00_docs"
        self.console = Console()
        self.refresh_interval = 5  # seconds
        
        # Load configuration
        self.config = self._load_config()
        
        # Monitoring state
        self.active_jobs = {}
        self.completed_jobs = []
        self.total_cost = 0.0
        self.asset_counts = {}
        self.sync_status = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load pipeline configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    async def get_video_generation_status(self) -> Dict[str, Any]:
        """Get status of all video generations (Gemini API + legacy Vertex AI)"""
        jobs_status = {
            "active": [],
            "completed": [],
            "failed": [],
            "total_cost": 0.0
        }
        
        # Check Gemini API generations from ledger
        ledger_path = self.project_root / "02_prompts" / "ledger.jsonl"
        if ledger_path.exists():
            async with aiofiles.open(ledger_path, 'r') as f:
                content = await f.read()
                for line in content.strip().split('\n'):
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            # Check if video file exists
                            video_path = self.project_root / "04_flow_exports" / f"{entry['scene']}_take{entry['take']:02d}_{entry['timestamp']}.mp4"
                            
                            job_info = {
                                "job_id": f"{entry['scene']}_take{entry['take']:02d}",
                                "scene": entry['scene'],
                                "timestamp": entry['timestamp'],
                                "status": "completed" if video_path.exists() else "active",
                                "cost": 0.15,  # Gemini API cost estimate per video
                                "api": "gemini"
                            }
                            
                            if job_info["status"] == "completed":
                                jobs_status["completed"].append(job_info)
                            else:
                                jobs_status["active"].append(job_info)
                            
                            jobs_status["total_cost"] += job_info["cost"]
                        except json.JSONDecodeError:
                            continue
        
        # Legacy Vertex AI jobs (if any exist)
        if self.vertex_jobs_dir.exists():
            for scene_dir in self.vertex_jobs_dir.iterdir():
                if scene_dir.is_dir():
                    for job_dir in scene_dir.iterdir():
                        if job_dir.is_dir():
                            metadata_file = job_dir / "metadata" / "job_metadata.json"
                            if metadata_file.exists():
                                async with aiofiles.open(metadata_file, 'r') as f:
                                    content = await f.read()
                                    metadata = json.loads(content)
                                    
                                    job_info = {
                                        "job_id": job_dir.name,
                                        "scene": scene_dir.name,
                                        "timestamp": metadata.get("timestamp"),
                                        "status": self._determine_job_status(job_dir),
                                        "cost": self._calculate_job_cost(metadata),
                                        "api": "vertex"
                                    }
                                    
                                    if job_info["status"] == "completed":
                                        jobs_status["completed"].append(job_info)
                                    elif job_info["status"] == "failed":
                                        jobs_status["failed"].append(job_info)
                                    else:
                                        jobs_status["active"].append(job_info)
                                    
                                    jobs_status["total_cost"] += job_info["cost"]
        
        return jobs_status
    
    def _determine_job_status(self, job_dir: Path) -> str:
        """Determine job status from directory contents"""
        outputs_dir = job_dir / "outputs"
        if outputs_dir.exists() and list(outputs_dir.glob("*.mp4")):
            return "completed"
        elif (job_dir / "metadata" / "error.log").exists():
            return "failed"
        else:
            return "active"
    
    def _calculate_job_cost(self, metadata: Dict[str, Any]) -> float:
        """Calculate job cost from metadata"""
        request = metadata.get("request_payload", {})
        instances = request.get("instances", [{}])
        if instances:
            duration = instances[0].get("duration", 5)
            resolution = instances[0].get("resolution", "1280x720")
            
            # Pricing based on resolution
            if "3840" in resolution or "4096" in resolution:
                rate = 0.15  # 4K
            elif "1920" in resolution:
                rate = 0.075  # 1080p
            else:
                rate = 0.0375  # 720p
            
            return duration * rate
        return 0.0
    
    async def get_asset_counts(self) -> Dict[str, int]:
        """Count assets in each directory"""
        counts = {
            "styleframes": len(list((self.project_root / "01_styleframes_midjourney").glob("*.*"))),
            "prompts": self._count_ledger_entries(),
            "vertex_jobs": len(list(self.vertex_jobs_dir.glob("*/*"))) if self.vertex_jobs_dir.exists() else 0,
            "flow_exports": len(list((self.project_root / "04_flow_exports").glob("*.mp4"))),
            "audio": len(list((self.project_root / "05_audio").glob("*.*"))),
            "final_cuts": len(list((self.project_root / "06_final_cut").glob("*.*")))
        }
        return counts
    
    def _count_ledger_entries(self) -> int:
        """Count entries in the prompt ledger"""
        ledger_path = self.project_root / "02_prompts" / "ledger.jsonl"
        if not ledger_path.exists():
            return 0
        
        try:
            with open(ledger_path, 'r') as f:
                return len([line for line in f if line.strip()])
        except:
            return 0
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Get GCS sync status from logs"""
        sync_logs_dir = self.logs_dir / "sync_logs"
        status = {
            "last_sync": "Never",
            "files_synced": 0,
            "files_skipped": 0,
            "next_sync": "Not scheduled"
        }
        
        if sync_logs_dir.exists():
            # Find most recent sync log
            logs = sorted(sync_logs_dir.glob("sync_*.log"), reverse=True)
            if logs:
                latest_log = logs[0]
                # Extract timestamp from filename
                timestamp_str = latest_log.stem.replace("sync_", "")
                try:
                    sync_time = datetime.strptime(timestamp_str, "%Y%m%dT%H%M%SZ")
                    status["last_sync"] = sync_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Parse log for stats
                    async with aiofiles.open(latest_log, 'r') as f:
                        content = await f.read()
                        lines = content.split('\n')
                        for line in lines:
                            if "uploaded/updated=" in line:
                                parts = line.split(",")
                                for part in parts:
                                    if "uploaded/updated=" in part:
                                        status["files_synced"] = int(part.split("=")[1])
                                    elif "skipped=" in part:
                                        status["files_skipped"] = int(part.split("=")[1])
                    
                    # Calculate next sync time (assuming hourly)
                    next_sync = sync_time + timedelta(hours=1)
                    status["next_sync"] = next_sync.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
        
        return status
    
    def create_dashboard_layout(self, jobs_status: Dict, asset_counts: Dict, 
                               sync_status: Dict) -> Layout:
        """Create rich dashboard layout"""
        layout = Layout()
        
        # Header
        header = Panel(
            Text("🎬 Stormlight Short - Production Pipeline Monitor", 
                 style="bold magenta", justify="center"),
            style="cyan"
        )
        
        # Jobs table
        jobs_table = Table(title="Video Generation Jobs", show_header=True, header_style="bold cyan")
        jobs_table.add_column("Scene", style="yellow")
        jobs_table.add_column("Job ID", style="dim")
        jobs_table.add_column("API", style="blue")
        jobs_table.add_column("Status", style="green")
        jobs_table.add_column("Cost", style="red")
        
        for job in jobs_status["active"]:
            api_emoji = "🔮" if job.get("api") == "gemini" else "☁️"
            jobs_table.add_row(
                job["scene"], 
                job["job_id"][:12] + "..." if len(job["job_id"]) > 15 else job["job_id"], 
                f"{api_emoji} {job.get('api', 'vertex').title()}",
                "🔄 Active", 
                f"${job['cost']:.2f}"
            )
        for job in jobs_status["completed"][-5:]:  # Last 5 completed
            api_emoji = "🔮" if job.get("api") == "gemini" else "☁️"
            jobs_table.add_row(
                job["scene"], 
                job["job_id"][:12] + "..." if len(job["job_id"]) > 15 else job["job_id"],
                f"{api_emoji} {job.get('api', 'vertex').title()}",
                "✅ Complete", 
                f"${job['cost']:.2f}"
            )
        
        # Assets table
        assets_table = Table(title="Asset Inventory", show_header=True, header_style="bold green")
        assets_table.add_column("Category", style="yellow")
        assets_table.add_column("Count", style="cyan")
        
        for category, count in asset_counts.items():
            assets_table.add_row(category.replace("_", " ").title(), str(count))
        
        # Sync status panel
        sync_text = f"""
Last Sync: {sync_status['last_sync']}
Files Synced: {sync_status['files_synced']}
Files Skipped: {sync_status['files_skipped']}
Next Sync: {sync_status['next_sync']}
        """
        sync_panel = Panel(sync_text, title="GCS Sync Status", style="blue")
        
        # Cost summary
        cost_text = f"""
Total Jobs: {len(jobs_status['active']) + len(jobs_status['completed']) + len(jobs_status['failed'])}
Active Jobs: {len(jobs_status['active'])}
Completed: {len(jobs_status['completed'])}
Failed: {len(jobs_status['failed'])}

Total Cost: ${jobs_status['total_cost']:.2f}
        """
        cost_panel = Panel(cost_text, title="Cost Summary", style="red")
        
        # Layout assembly - create named layouts for proper rendering
        layout.split_column(
            Layout(header, size=3, name="header"),
            Layout(name="body")
        )
        
        # Split the body into two columns
        layout["body"].split_row(
            Layout(jobs_table, name="jobs"),
            Layout(name="sidebar")
        )
        
        # Split the sidebar into three panels
        layout["body"]["sidebar"].split_column(
            Layout(assets_table, name="assets"),
            Layout(sync_panel, name="sync"),
            Layout(cost_panel, name="cost")
        )
        
        return layout
    
    async def run_dashboard(self):
        """Run the live monitoring dashboard"""
        with Live(console=self.console, refresh_per_second=1) as live:
            while True:
                try:
                    # Gather all monitoring data
                    jobs_status = await self.get_video_generation_status()
                    asset_counts = await self.get_asset_counts()
                    sync_status = await self.get_sync_status()
                    
                    # Create and update dashboard
                    layout = self.create_dashboard_layout(jobs_status, asset_counts, sync_status)
                    live.update(layout)
                    
                    # Wait before refresh
                    await asyncio.sleep(self.refresh_interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[red]Error updating dashboard: {e}[/red]")
                    await asyncio.sleep(self.refresh_interval)
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of the pipeline"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Check GCP authentication
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--format=json"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                health["checks"]["gcp_auth"] = "✅ Authenticated"
            else:
                health["checks"]["gcp_auth"] = "❌ Not authenticated"
                health["status"] = "warning"
        except:
            health["checks"]["gcp_auth"] = "❌ gcloud not found"
            health["status"] = "critical"
        
        # Check directory structure
        required_dirs = [
            "00_docs", "01_styleframes_midjourney", "02_prompts",
            "03_vertex_jobs", "04_flow_exports", "05_audio", "06_final_cut"
        ]
        missing_dirs = []
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            health["checks"]["directories"] = f"⚠️ Missing: {', '.join(missing_dirs)}"
            health["status"] = "warning" if health["status"] == "healthy" else health["status"]
        else:
            health["checks"]["directories"] = "✅ All directories present"
        
        # Check Python dependencies
        try:
            import google.generativeai as genai
            health["checks"]["gemini_api"] = "✅ Gemini API available"
        except ImportError:
            health["checks"]["gemini_api"] = "❌ Missing google-generativeai"
            health["status"] = "critical"
        
        # Check Gemini API key
        import os
        if os.getenv("GEMINI_API_KEY"):
            health["checks"]["api_key"] = "✅ Gemini API key set"
        else:
            health["checks"]["api_key"] = "❌ GEMINI_API_KEY not set"
            health["status"] = "warning" if health["status"] == "healthy" else health["status"]
        
        # Check legacy dependencies (optional)
        try:
            import google.cloud.storage
            import google.cloud.aiplatform
            health["checks"]["legacy_gcp"] = "✅ Legacy GCP libs available"
        except ImportError:
            health["checks"]["legacy_gcp"] = "⚠️ Legacy GCP libs missing (optional)"
        
        # Check configuration
        if self.config_path.exists():
            if self.config.get("gcp_project_id") == "your-project-id":
                health["checks"]["config"] = "⚠️ Config needs update"
                health["status"] = "warning" if health["status"] == "healthy" else health["status"]
            else:
                health["checks"]["config"] = "✅ Configured"
        else:
            health["checks"]["config"] = "❌ No config file"
            health["status"] = "critical"
        
        return health
    
    async def run_status_report(self):
        """Run one-time status report"""
        jobs_status = await self.get_video_generation_status()
        asset_counts = await self.get_asset_counts()
        sync_status = await self.get_sync_status()
        
        console.print("\n📊 Pipeline Status Report\n", style="bold cyan")
        console.print(f"Video Jobs: {len(jobs_status['active'])} active, {len(jobs_status['completed'])} completed")
        console.print(f"Total Cost: ${jobs_status['total_cost']:.2f}")
        console.print(f"Assets: {sum(asset_counts.values())} total files")
        console.print(f"Generated Videos: {asset_counts['flow_exports']} MP4 files")
        console.print(f"Prompt Entries: {asset_counts['prompts']} logged")
        console.print(f"Last Sync: {sync_status['last_sync']}")


def main():
    """CLI interface for pipeline monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline Monitor for Stormlight Short")
    parser.add_argument("--dashboard", action="store_true", help="Run live dashboard")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--refresh", type=int, default=5, help="Dashboard refresh interval (seconds)")
    
    args = parser.parse_args()
    
    monitor = PipelineMonitor()
    monitor.refresh_interval = args.refresh
    
    if args.health_check:
        health = monitor.run_health_check()
        console.print("\n🏥 Pipeline Health Check\n", style="bold cyan")
        
        status_color = "green" if health["status"] == "healthy" else "yellow" if health["status"] == "warning" else "red"
        console.print(f"Overall Status: {health['status'].upper()}", style=f"bold {status_color}")
        console.print(f"Timestamp: {health['timestamp']}\n")
        
        for check, result in health["checks"].items():
            console.print(f"{check}: {result}")
        
    elif args.dashboard:
        console.print("Starting Pipeline Monitor Dashboard...", style="bold green")
        console.print("Press Ctrl+C to exit\n")
        asyncio.run(monitor.run_dashboard())
    else:
        # Run one-time status report
        asyncio.run(monitor.run_status_report())


if __name__ == "__main__":
    main()