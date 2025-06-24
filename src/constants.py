"""
Constants and enums for Wanderer Finance application.

This module defines all constants, enums, and magic values used throughout
the application to improve maintainability and reduce errors.
"""

from enum import Enum
from typing import Final


class TradingAction(Enum):
    """Enumeration of possible trading actions."""
    
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


class EvaluationResult(Enum):
    """Enumeration of evaluation results."""
    
    WIN = "WIN"
    LOSS = "LOSS"


class Sentiment(Enum):
    """Enumeration of sentiment values."""
    
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class MarketStatus(Enum):
    """Enumeration of market status values."""
    
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    HOLIDAY = "HOLIDAY"


# Database constants
DB_TABLE_NAME: Final[str] = "data"
DB_BATCH_SIZE: Final[int] = 100

# API constants
MAX_RETRIES: Final[int] = 3
REQUEST_TIMEOUT: Final[int] = 30
RATE_LIMIT_DELAY: Final[float] = 1.0

# Trading constants
MAX_ARTICLES_PER_STOCK: Final[int] = 2
TRADING_SESSION_START: Final[str] = "09:30"
TRADING_SESSION_END: Final[str] = "16:00"

# UI constants
DEFAULT_TICKER_OPTION: Final[str] = "select ticker"
REFRESH_BUTTON_TEXT: Final[str] = "Refresh Data"
ERROR_MESSAGE_PREFIX: Final[str] = "Error: "

# File paths
LOG_FILE_PATH: Final[str] = "logs/wanderer.log"
CACHE_DIR: Final[str] = ".cache"

# Validation constants
MIN_STOCK_PRICE: Final[float] = 0.01
MAX_STOCK_PRICE: Final[float] = 10000.0
MIN_PERCENT_CHANGE: Final[float] = -100.0
MAX_PERCENT_CHANGE: Final[float] = 1000.0

# LLM constants
DEFAULT_TEMPERATURE: Final[float] = 0.1
MAX_TOKENS: Final[int] = 4000
PROMPT_TIMEOUT: Final[int] = 60

# Date format constants
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT: Final[str] = "%B %d, %Y"
