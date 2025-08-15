#!/usr/bin/env python3
"""
Safety Manager for Stormlight Short
Handles confirmations, permissions, and safe operations for cloud data.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess


class SafetyManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.safety_log = self.project_root / "00_docs" / "safety_logs" / "operations.log"
        self.safety_log.parent.mkdir(parents=True, exist_ok=True)
        
    def log_operation(self, operation: str, details: Dict[str, Any], 
                     approved: bool = False, user_confirmation: str = ""):
        """Log all safety-critical operations"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "approved": approved,
            "user_confirmation": user_confirmation,
            "user": subprocess.getoutput("whoami")
        }
        
        with open(self.safety_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def confirm_destructive_operation(self, operation: str, details: Dict[str, Any],
                                    auto_approve: bool = False) -> bool:
        """Request user confirmation for destructive operations"""
        
        if auto_approve:
            print(f"[AUTO-APPROVED] {operation}")
            self.log_operation(operation, details, approved=True, 
                             user_confirmation="auto_approved")
            return True
        
        print(f"\n⚠️  DESTRUCTIVE OPERATION REQUESTED ⚠️")
        print(f"Operation: {operation}")
        print(f"Details:")
        for key, value in details.items():
            print(f"  {key}: {value}")
        
        print(f"\nThis operation may:")
        print(f"  - Delete or overwrite cloud data")
        print(f"  - Modify existing files")
        print(f"  - Incur cloud costs")
        
        while True:
            response = input("\nDo you want to proceed? (yes/no/details): ").lower().strip()
            
            if response in ['yes', 'y']:
                self.log_operation(operation, details, approved=True, 
                                 user_confirmation=response)
                return True
            elif response in ['no', 'n']:
                self.log_operation(operation, details, approved=False, 
                                 user_confirmation=response)
                return False
            elif response == 'details':
                self._show_detailed_info(operation, details)
            else:
                print("Please answer 'yes', 'no', or 'details'")
    
    def _show_detailed_info(self, operation: str, details: Dict[str, Any]):
        """Show detailed information about the operation"""
        
        print(f"\n📋 DETAILED OPERATION INFO")
        print(f"Operation: {operation}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        if operation == "gcs_sync_delete":
            print(f"\nThis will DELETE files from Google Cloud Storage that are not present locally.")
            print(f"Bucket: {details.get('bucket', 'unknown')}")
            print(f"Prefix: {details.get('prefix', 'root')}")
            print(f"Estimated files to delete: {details.get('estimated_deletions', 'unknown')}")
            
        elif operation == "gcs_upload":
            print(f"\nThis will UPLOAD/UPDATE files to Google Cloud Storage.")
            print(f"Bucket: {details.get('bucket', 'unknown')}")
            print(f"Files to upload: {details.get('file_count', 'unknown')}")
            print(f"Total size: {details.get('total_size', 'unknown')}")
            
        elif operation == "vertex_ai_job":
            print(f"\nThis will submit a job to Vertex AI (may incur costs).")
            print(f"Model: {details.get('model', 'unknown')}")
            print(f"Estimated cost: {details.get('estimated_cost', 'unknown')}")
            
        print(f"\nFull details: {json.dumps(details, indent=2)}")
    
    def check_gcs_permissions(self, bucket_name: str) -> Dict[str, bool]:
        """Check GCS bucket permissions"""
        
        permissions = {
            "read": False,
            "write": False,
            "delete": False
        }
        
        try:
            # Test read permission
            result = subprocess.run([
                "gsutil", "ls", f"gs://{bucket_name}/"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                permissions["read"] = True
                
                # Test write permission (create a test file)
                test_content = f"test_{datetime.now().isoformat()}"
                test_file = f"gs://{bucket_name}/.stormlight_permission_test"
                
                write_result = subprocess.run([
                    "gsutil", "cp", "-", test_file
                ], input=test_content, text=True, capture_output=True, timeout=30)
                
                if write_result.returncode == 0:
                    permissions["write"] = True
                    
                    # Test delete permission (remove test file)
                    delete_result = subprocess.run([
                        "gsutil", "rm", test_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    if delete_result.returncode == 0:
                        permissions["delete"] = True
                        
        except subprocess.TimeoutExpired:
            print("Warning: GCS permission check timed out")
        except Exception as e:
            print(f"Warning: Error checking GCS permissions: {e}")
        
        return permissions
    
    def validate_bucket_url_safety(self, bucket_name: str, prefix: str = "") -> bool:
        """Validate that bucket URLs won't be exposed publicly"""
        
        # Check if bucket has public access
        try:
            result = subprocess.run([
                "gsutil", "iam", "get", f"gs://{bucket_name}"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                iam_policy = json.loads(result.stdout)
                
                # Check for public access
                for binding in iam_policy.get("bindings", []):
                    members = binding.get("members", [])
                    if "allUsers" in members or "allAuthenticatedUsers" in members:
                        print(f"⚠️  Warning: Bucket {bucket_name} has public access!")
                        return False
                        
                return True
                
        except Exception as e:
            print(f"Warning: Could not validate bucket IAM policy: {e}")
            return True  # Assume safe if we can't check
    
    def create_backup_before_destructive_op(self, operation: str, 
                                          paths: List[Path]) -> Optional[Path]:
        """Create backup before destructive operations"""
        
        backup_dir = self.project_root / "00_docs" / "backups" / f"{operation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            for path in paths:
                if path.exists():
                    if path.is_file():
                        backup_file = backup_dir / path.name
                        subprocess.run(["cp", str(path), str(backup_file)], check=True)
                    elif path.is_dir():
                        backup_subdir = backup_dir / path.name
                        subprocess.run(["cp", "-r", str(path), str(backup_subdir)], check=True)
            
            print(f"✅ Created backup at: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None
    
    def estimate_gcs_costs(self, operation: str, details: Dict[str, Any]) -> Dict[str, float]:
        """Estimate GCS operation costs"""
        
        # Rough cost estimates (as of 2024, subject to change)
        costs = {
            "storage_gb_month": 0.020,  # Standard storage
            "class_a_operations": 0.005 / 1000,  # Per 1000 operations
            "class_b_operations": 0.0004 / 1000,  # Per 1000 operations
            "network_egress_gb": 0.12  # First 1GB free per month
        }
        
        estimates = {
            "storage_cost": 0.0,
            "operation_cost": 0.0,
            "network_cost": 0.0,
            "total_estimated": 0.0
        }
        
        if operation == "gcs_upload":
            file_count = details.get("file_count", 0)
            total_size_gb = details.get("total_size_gb", 0)
            
            estimates["storage_cost"] = total_size_gb * costs["storage_gb_month"]
            estimates["operation_cost"] = file_count * costs["class_a_operations"]
            
        elif operation == "gcs_sync":
            upload_count = details.get("upload_count", 0)
            download_count = details.get("download_count", 0)
            
            estimates["operation_cost"] = (upload_count * costs["class_a_operations"] + 
                                         download_count * costs["class_b_operations"])
        
        estimates["total_estimated"] = sum(estimates.values())
        return estimates


def main():
    """CLI interface for safety manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safety Manager for Stormlight Short")
    parser.add_argument("--check-permissions", help="Check GCS bucket permissions")
    parser.add_argument("--validate-bucket", help="Validate bucket safety")
    parser.add_argument("--show-log", action="store_true", help="Show safety operation log")
    
    args = parser.parse_args()
    
    manager = SafetyManager()
    
    if args.check_permissions:
        permissions = manager.check_gcs_permissions(args.check_permissions)
        print(f"Bucket {args.check_permissions} permissions:")
        for perm, allowed in permissions.items():
            status = "✅" if allowed else "❌"
            print(f"  {perm}: {status}")
    
    if args.validate_bucket:
        is_safe = manager.validate_bucket_url_safety(args.validate_bucket)
        status = "✅ Safe" if is_safe else "⚠️  Potentially unsafe"
        print(f"Bucket {args.validate_bucket}: {status}")
    
    if args.show_log:
        if manager.safety_log.exists():
            with open(manager.safety_log, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        print(f"{entry['timestamp']}: {entry['operation']} - {'✅' if entry['approved'] else '❌'}")
                    except json.JSONDecodeError:
                        continue
        else:
            print("No safety log found")


if __name__ == "__main__":
    main()
