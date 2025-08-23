"""
Utility functions for the Pirate OSINT Telegram Bot.
"""

import re
import logging
import sys
from typing import Optional

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    # Set specific logger levels
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

def is_valid_phone_number(text: str) -> bool:
    """
    Check if text looks like a phone number.
    
    Args:
        text: Input text to validate
        
    Returns:
        True if text appears to be a phone number
    """
    if not text or not isinstance(text, str):
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', text.strip())
    
    # Check for basic phone number patterns
    patterns = [
        r'^\+?[1-9]\d{7,14}$',  # International format
        r'^\d{10,15}$',          # Basic numeric format
        r'^\+?\d{1,4}\d{7,14}$'  # Country code + number
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)

def format_phone_number(phone_number: str) -> str:
    """
    Format phone number for API requests.
    
    Args:
        phone_number: Raw phone number input
        
    Returns:
        Formatted phone number
    """
    if not phone_number or not isinstance(phone_number, str):
        return ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number.strip())
    
    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Ensure we have only digits
    if not cleaned.isdigit():
        return phone_number.strip()  # Return original if can't clean
    
    return cleaned

def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram Markdown.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Markdown
    """
    if not text or not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Characters that need escaping in Telegram Markdown
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    escaped = text
    for char in escape_chars:
        escaped = escaped.replace(char, f'\\{char}')
    
    return escaped

def truncate_text(text: str, max_length: int = 4000) -> str:
    """
    Truncate text to fit Telegram message limits.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (default 4000, leaving room for formatting)
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def validate_environment():
    """
    Validate required environment variables.
    
    Returns:
        Tuple of (is_valid, missing_vars)
    """
    import os
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input for logging and display.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potential control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    sanitized = truncate_text(sanitized, 200)
    
    return sanitized.strip()

class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier."""
        import time
        from collections import deque
        
        now = time.time()
        window_start = now - self.window_seconds
        
        if identifier not in self.requests:
            self.requests[identifier] = deque()
        
        user_requests = self.requests[identifier]
        
        # Remove old requests
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Check limit
        if len(user_requests) >= self.max_requests:
            return False
        
        # Add current request
        user_requests.append(now)
        return True
