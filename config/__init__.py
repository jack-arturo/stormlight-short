"""
Configuration Module for Stormlight Short Pipeline

This module manages all configuration settings for the pipeline including:
- Pipeline configuration (pipeline_config.yaml)
- Environment variables
- API keys and credentials
- Processing parameters
- Output settings
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration file path
CONFIG_PATH = Path(__file__).parent / "pipeline_config.yaml"

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load pipeline configuration from YAML file.
    
    Args:
        config_path: Optional path to config file, defaults to pipeline_config.yaml
        
    Returns:
        Dictionary containing configuration settings
    """
    if config_path is None:
        config_path = CONFIG_PATH
        
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """
    Save pipeline configuration to YAML file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Optional path to save config file, defaults to pipeline_config.yaml
    """
    if config_path is None:
        config_path = CONFIG_PATH
        
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

# Default configuration
DEFAULT_CONFIG = {
    "gcp_project_id": "",
    "gcs_bucket": "",
    "vertex_region": "us-central1",
    "midjourney": {
        "max_concurrent_jobs": 3,
        "retry_attempts": 3,
        "timeout_seconds": 300
    },
    "sync": {
        "check_interval_seconds": 30,
        "batch_size": 10,
        "max_retries": 3
    },
    "safety": {
        "content_filtering": True,
        "max_file_size_mb": 100,
        "allowed_extensions": [".jpg", ".jpeg", ".png", ".mp4", ".mov"]
    },
    "pipeline": {
        "output_format": "mp4",
        "quality": "high",
        "frame_rate": 24
    }
}

__all__ = [
    "load_config",
    "save_config", 
    "DEFAULT_CONFIG",
    "CONFIG_PATH"
]