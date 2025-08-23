#!/usr/bin/env python3
"""
Pirate OSINT Telegram Bot
A Telegram bot that integrates with pirate-osint API for OSINT lookups and intelligence gathering.
"""

import os
import logging
import sys
from datetime import datetime

import telebot
from telebot import types, apihelper

from config import Config
from bot_handlers import BotHandlers
from utils import setup_logging

def main():
    """Main function to initialize and run the bot."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config = Config()
    
    # Validate required environment variables
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    if not config.PIRATE_OSINT_API_KEY:
        logger.error("PIRATE_OSINT_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Enable middleware support
    apihelper.ENABLE_MIDDLEWARE = True
    
    # Initialize bot
    try:
        bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)
        logger.info("Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        sys.exit(1)
    
    # Initialize handlers
    handlers = BotHandlers(bot, config)
    
    # Register command handlers
    @bot.message_handler(commands=['start'])
    def start_command(message):
        handlers.handle_start(message)
    
    @bot.message_handler(commands=['help'])
    def help_command(message):
        handlers.handle_help(message)
    
    @bot.message_handler(commands=['lookup'])
    def lookup_command(message):
        handlers.handle_lookup(message)
    
    @bot.message_handler(commands=['status'])
    def status_command(message):
        handlers.handle_status(message)
    
    # Handle text messages for interactive lookup
    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def handle_text(message):
        handlers.handle_text_message(message)
    
    # Handle button clicks
    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        handlers.handle_callback_query(call)
    
    # Error handler
    @bot.middleware_handler(update_types=['message'])
    def error_handler(bot_instance, message):
        try:
            return True
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            bot.send_message(
                message.chat.id,
                "❌ An error occurred while processing your request. Please try again later."
            )
            return False
    
    # Start bot
    logger.info("Starting bot...")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=30)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
