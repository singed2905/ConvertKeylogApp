"""Configuration management for ConvertKeylogApp."""

import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.config_dir = Path("config")
        self._configs = {}
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = self.config_dir / f"{config_name}.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Save configuration to JSON file."""
        config_path = self.config_dir / f"{config_name}.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
