"""
Configuration Management Module
Handles app settings, environment variables, and configuration loading
"""

import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    """Application configuration dataclass"""
    # LLM Settings
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.1
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Cache Settings
    cache_ttl_hours: int = 24
    cache_enabled: bool = True
    
    # Database Settings
    db_path: str = "data/diagnostics.db"
    logs_path: str = "data/logs"
    
    # Vision Settings
    vision_enabled: bool = True
    vision_timeout: int = 15
    
    # Agent Settings
    agent_timeout: int = 60
    stream_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables"""
        return cls(
            model_name=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            temperature=float(os.getenv("LLM_TEMPERATURE", 0.1)),
            max_retries=int(os.getenv("MAX_RETRIES", 3)),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", 30)),
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            db_path=os.getenv("DB_PATH", "data/diagnostics.db"),
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> "AppConfig":
        """Load configuration from YAML file"""
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if not (0 <= self.temperature <= 1):
            raise ValueError("Temperature must be between 0 and 1")
        if self.max_retries < 1:
            raise ValueError("Max retries must be at least 1")
        if self.timeout_seconds < 5:
            raise ValueError("Timeout must be at least 5 seconds")
        return True


# Global config instance
CONFIG = AppConfig.from_env()
CONFIG.validate()
