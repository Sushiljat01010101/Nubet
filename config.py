"""
Configuration module for the Pirate OSINT Telegram Bot.
"""

import os
from typing import List, Optional

class Config:
    """Configuration class to manage environment variables and settings."""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
        
        # Pirate OSINT API Configuration
        self.PIRATE_OSINT_API_KEY: str = os.getenv('PIRATE_OSINT_API_KEY', 'kQ5hlafjxfgJTJ5d')
        self.PIRATE_OSINT_BASE_URL: str = os.getenv('PIRATE_OSINT_BASE_URL', 'http://pirate-osint.onrender.com/api')
        
        # Bot Configuration
        self.ADMIN_IDS: List[int] = self._parse_admin_ids()
        self.RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '5'))
        self.RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE: Optional[str] = os.getenv('LOG_FILE', 'bot.log')
        
        # API Timeout Configuration
        self.API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
        
        # Bot Messages
        self.WELCOME_MESSAGE = """
🏴‍☠️ **Welcome to Pirate OSINT Bot!**

This bot helps you perform OSINT (Open Source Intelligence) lookups using phone numbers and other identifiers.

**Available Commands:**
/start - Show this welcome message
/help - Display detailed help information
/lookup <number> - Perform OSINT lookup on a phone number
/status - Check bot and API status

**Example:**
/lookup +1234567890
or
/lookup 1234567890

⚠️ **Important:** Use this bot responsibly and in accordance with local laws and regulations.
        """
        
        self.HELP_MESSAGE = """
🏴‍☠️ **Pirate OSINT Bot Help**

**Commands:**
• `/start` - Welcome message and basic info
• `/help` - This help message
• `/lookup <number>` - Perform OSINT lookup
• `/status` - Check system status

**Usage Examples:**
• `/lookup +1234567890`
• `/lookup 1234567890`
• Simply send a phone number as a message

**Supported Formats:**
• International format: +1234567890
• National format: 1234567890
• With spaces/dashes: +1-234-567-8900

**Rate Limits:**
• Maximum {rate_limit} requests per {window} seconds
• Please wait between requests

**Privacy & Security:**
• We don't store your queries
• All lookups are logged for security
• Use responsibly and legally

Need more help? Contact the bot administrator.
        """.format(rate_limit=self.RATE_LIMIT_REQUESTS, window=self.RATE_LIMIT_WINDOW)
    
    def _parse_admin_ids(self) -> List[int]:
        """Parse admin IDs from environment variable."""
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        if not admin_ids_str:
            return []
        
        try:
            return [int(id_str.strip()) for id_str in admin_ids_str.split(',') if id_str.strip()]
        except ValueError:
            return []
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an administrator."""
        return user_id in self.ADMIN_IDS
    
    def get_api_url(self) -> str:
        """Get the complete API URL with key."""
        return f"{self.PIRATE_OSINT_BASE_URL}?key={self.PIRATE_OSINT_API_KEY}"
