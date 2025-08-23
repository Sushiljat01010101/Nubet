# Pirate OSINT Telegram Bot

## Overview

This is a Telegram bot that integrates with the Pirate OSINT API to perform Open Source Intelligence (OSINT) lookups on phone numbers. The bot provides a user-friendly interface for intelligence gathering while implementing rate limiting and proper error handling to ensure responsible usage.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
The application follows a modular architecture with clear separation of concerns:

- **Main Entry Point** (`main.py`): Handles bot initialization, environment validation, and command registration
- **Bot Handlers** (`bot_handlers.py`): Manages all message processing, command handling, and user interactions
- **API Integration** (`osint_api.py`): Provides abstracted interface to the Pirate OSINT external API
- **Configuration Management** (`config.py`): Centralizes all environment variables and bot settings
- **Utilities** (`utils.py`): Contains shared helper functions for logging, validation, and formatting

### Rate Limiting System
Implements a sliding window rate limiting mechanism using in-memory storage:
- Uses `collections.deque` for efficient time-based request tracking
- Configurable request limits and time windows
- Per-user rate limiting to prevent abuse

### User State Management
Maintains user interaction states using in-memory dictionaries to track conversation flow and command contexts.

### Error Handling and Logging
- Comprehensive logging system with configurable levels and file output
- Structured error handling with user-friendly error messages
- API timeout configurations to prevent hanging requests

### Phone Number Processing
- Phone number validation and formatting utilities
- Support for various international phone number formats
- Input sanitization to ensure API compatibility

## External Dependencies

### Third-Party APIs
- **Pirate OSINT API**: External OSINT service for phone number intelligence gathering
  - Base URL: `http://pirate-osint.onrender.com/api`
  - Requires API key authentication
  - Supports phone number lookup functionality

### Python Libraries
- **pyTelegramBotAPI (telebot)**: Telegram Bot API wrapper for bot functionality
- **requests**: HTTP client library for external API communication
- **urllib.parse**: URL encoding for API parameters

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Required Telegram bot token
- `PIRATE_OSINT_API_KEY`: Required API key for OSINT service
- `PIRATE_OSINT_BASE_URL`: Optional base URL override
- `ADMIN_IDS`: Optional comma-separated admin user IDs
- `RATE_LIMIT_REQUESTS`: Configurable rate limit (default: 5)
- `RATE_LIMIT_WINDOW`: Configurable time window in seconds (default: 60)
- `LOG_LEVEL`: Logging verbosity level
- `LOG_FILE`: Optional log file path
- `API_TIMEOUT`: API request timeout in seconds (default: 30)

### Infrastructure Requirements
- No database dependencies (uses in-memory storage)
- Requires internet connectivity for Telegram API and external OSINT API
- Suitable for containerized deployment environments