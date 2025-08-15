#!/usr/bin/env python3
"""
Setup Script for Stormlight Short Pipeline
Initializes the complete development environment.
"""

import subprocess
import sys
from pathlib import Path
import yaml
import json


def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check gcloud
    try:
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud SDK installed")
        else:
            print("❌ Google Cloud SDK not found")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud SDK not found")
        return False
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def setup_directories():
    """Create all required directories"""
    print("📁 Setting up directory structure...")
    
    directories = [
        "00_docs/sync_logs",
        "00_docs/safety_logs", 
        "00_docs/backups",
        "01_styleframes_midjourney",
        "02_prompts",
        "03_vertex_jobs",
        "04_flow_exports",
        "05_audio",
        "06_final_cut",
        "config"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")
    return True


def setup_configuration():
    """Set up initial configuration"""
    print("⚙️  Setting up configuration...")
    
    config_path = Path("config/pipeline_config.yaml")
    
    if config_path.exists():
        print("✅ Configuration already exists")
        return True
    
    # Get user input for configuration
    print("\n📝 Please provide configuration details:")
    
    gcp_project = input("GCP Project ID: ").strip()
    if not gcp_project:
        print("❌ GCP Project ID is required")
        return False
    
    gcs_bucket = input("GCS Bucket Name: ").strip()
    if not gcs_bucket:
        print("❌ GCS Bucket Name is required")
        return False
    
    # Update config file
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    config['gcp_project_id'] = gcp_project
    config['gcs_bucket'] = gcs_bucket
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Configuration updated")
    return True


def test_gcp_authentication():
    """Test GCP authentication"""
    print("🔐 Testing GCP authentication...")
    
    try:
        result = subprocess.run([
            "gcloud", "auth", "application-default", "print-access-token"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GCP authentication working")
            return True
        else:
            print("❌ GCP authentication failed")
            print("Run: gcloud auth application-default login")
            return False
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False


def test_gcs_access():
    """Test GCS bucket access"""
    print("☁️  Testing GCS bucket access...")
    
    config_path = Path("config/pipeline_config.yaml")
    if not config_path.exists():
        print("❌ Configuration not found")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    bucket = config.get('gcs_bucket')
    if not bucket:
        print("❌ No bucket configured")
        return False
    
    try:
        result = subprocess.run([
            "gsutil", "ls", f"gs://{bucket}/"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GCS bucket accessible")
            return True
        else:
            print(f"❌ Cannot access bucket gs://{bucket}/")
            print("Check bucket name and permissions")
            return False
    except Exception as e:
        print(f"❌ Error testing bucket access: {e}")
        return False


def run_tests():
    """Run pipeline tests"""
    print("🧪 Running pipeline tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "tools/test_pipeline.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def create_sample_data():
    """Create sample data for testing"""
    print("📄 Creating sample data...")
    
    # Create sample scene data
    sample_scene = {
        "scene_name": "sample_scene",
        "created": "2024-12-15T12:00:00",
        "entries": [
            {
                "take_number": 1,
                "timestamp": "2024-12-15T12:00:00",
                "prompt_text": "Sample prompt for testing",
                "seed": 12345,
                "source": "Manual",
                "metadata": {"test": True}
            }
        ]
    }
    
    sample_ledger_path = Path("02_prompts/sample_scene_ledger.json")
    with open(sample_ledger_path, 'w') as f:
        json.dump(sample_scene, f, indent=2)
    
    print("✅ Sample data created")
    return True


def setup_automation():
    """Set up automation (optional)"""
    print("🤖 Setting up automation...")
    
    response = input("Set up automated sync? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        schedule_type = "launchd" if sys.platform == "darwin" else "cron"
        
        try:
            result = subprocess.run([
                sys.executable, "tools/automation_orchestrator.py",
                "--setup-schedule", schedule_type
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {schedule_type} automation set up")
                return True
            else:
                print(f"❌ Failed to set up {schedule_type} automation")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error setting up automation: {e}")
            return False
    else:
        print("⏭️  Skipping automation setup")
        return True


def main():
    """Main setup process"""
    print("🎬 Stormlight Short Pipeline Setup")
    print("=" * 50)
    
    steps = [
        ("System Requirements", check_requirements),
        ("Dependencies", install_dependencies),
        ("Directory Structure", setup_directories),
        ("Configuration", setup_configuration),
        ("GCP Authentication", test_gcp_authentication),
        ("GCS Access", test_gcs_access),
        ("Pipeline Tests", run_tests),
        ("Sample Data", create_sample_data),
        ("Automation", setup_automation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    print(f"\n{'='*50}")
    print("🎯 SETUP SUMMARY")
    print(f"{'='*50}")
    
    if failed_steps:
        print("❌ Setup completed with issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve these issues before using the pipeline.")
    else:
        print("✅ Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Test sync: python3 tools/sync_to_gcs.py.py --local . --bucket your-bucket --dry-run")
        print("2. Create Vertex AI job: python3 tools/vertex_manager.py --help")
        print("3. Process style frames: python3 tools/midjourney_manager.py --help")
        print("4. Read documentation: 00_docs/README.md")
    
    return len(failed_steps) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
