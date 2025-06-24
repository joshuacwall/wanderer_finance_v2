"""
Configuration management for Wanderer Finance application.

This module provides centralized configuration management using environment variables
with sensible defaults and validation.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    path: str = "main.db"
    table_name: str = "data"
    
    @property
    def absolute_path(self) -> str:
        """Get absolute path to database file."""
        return os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                self.path
            )
        )


@dataclass
class LLMConfig:
    """Large Language Model configuration settings."""
    
    model: str = "groq/deepseek-r1-distill-llama-70b"
    temperature: float = 0.1
    max_retries: int = 3
    timeout: int = 30


@dataclass
class APIConfig:
    """External API configuration settings."""
    
    alpha_vantage_key: Optional[str] = None
    news_data_key: Optional[str] = None
    
    def __post_init__(self):
        """Load API keys from environment variables."""
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.news_data_key = os.getenv("NEWS_DATA_API_KEY")


@dataclass
class TradingConfig:
    """Trading strategy configuration settings."""
    
    max_articles_per_stock: int = 2
    analysis_timeout: int = 60
    market_check_enabled: bool = True


@dataclass
class UIConfig:
    """User interface configuration settings."""
    
    gradio_share: bool = False
    gradio_debug: bool = False
    refresh_interval: int = 300  # seconds


@dataclass
class AppConfig:
    """Main application configuration."""
    
    database: DatabaseConfig
    llm: LLMConfig
    api: APIConfig
    trading: TradingConfig
    ui: UIConfig
    
    def __init__(self):
        """Initialize all configuration sections."""
        self.database = DatabaseConfig()
        self.llm = LLMConfig()
        self.api = APIConfig()
        self.trading = TradingConfig()
        self.ui = UIConfig()


# Global configuration instance
config = AppConfig()
