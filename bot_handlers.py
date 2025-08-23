"""
Bot message handlers for the Pirate OSINT Telegram Bot.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict, deque

import telebot
from telebot import types

from config import Config
from osint_api import PirateOSINTAPI
from utils import format_phone_number, is_valid_phone_number, escape_markdown

class BotHandlers:
    """Handles all bot message processing and commands."""
    
    def __init__(self, bot: telebot.TeleBot, config: Config):
        self.bot = bot
        self.config = config
        self.api = PirateOSINTAPI(config)
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting storage
        self.rate_limiter: Dict[int, deque] = defaultdict(deque)
        
        # User state management
        self.user_states: Dict[int, str] = {}
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limits."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.config.RATE_LIMIT_WINDOW)
        
        # Clean old requests
        user_requests = self.rate_limiter[user_id]
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Check if limit exceeded
        if len(user_requests) >= self.config.RATE_LIMIT_REQUESTS:
            return False
        
        # Add current request
        user_requests.append(now)
        return True
    
    def _send_rate_limit_message(self, chat_id: int):
        """Send rate limit exceeded message."""
        message = f"""
⏰ **Rate Limit Exceeded**

You can only make {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW} seconds.

Please wait before making another request.
        """
        self.bot.send_message(chat_id, message, parse_mode='Markdown')
    
    def handle_start(self, message):
        """Handle /start command."""
        try:
            user_info = f"User: {message.from_user.first_name} ({message.from_user.id})"
            self.logger.info(f"Start command received from {user_info}")
            
            # Create attractive welcome message
            welcome_text = """
🏴‍☠️ **Welcome to Pirate OSINT Bot!**

Your ultimate tool for OSINT phone number lookups and intelligence gathering.

🔍 **What can I do?**
• Phone number intelligence gathering
• Contact information lookup
• Address & network details
• Fast and secure searches

🚀 **Get Started:**
Choose an option below or simply send me a phone number!
            """
            
            # Create main menu with attractive buttons
            markup = types.InlineKeyboardMarkup(row_width=2)
            lookup_btn = types.InlineKeyboardButton("🔍 Search Number", callback_data="lookup")
            help_btn = types.InlineKeyboardButton("📖 Help", callback_data="help")
            status_btn = types.InlineKeyboardButton("📊 Bot Status", callback_data="status")
            examples_btn = types.InlineKeyboardButton("💡 Examples", callback_data="examples")
            markup.add(lookup_btn)
            markup.add(help_btn, status_btn)
            markup.add(examples_btn)
            
            self.bot.send_message(
                message.chat.id,
                welcome_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in handle_start: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ An error occurred. Please try again later."
            )
    
    def handle_help(self, message):
        """Handle /help command."""
        try:
            user_info = f"User: {message.from_user.first_name} ({message.from_user.id})"
            self.logger.info(f"Help command received from {user_info}")
            
            self.bot.send_message(
                message.chat.id,
                self.config.HELP_MESSAGE,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in handle_help: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ An error occurred. Please try again later."
            )
    
    def handle_lookup(self, message):
        """Handle /lookup command."""
        try:
            user_id = message.from_user.id
            user_info = f"User: {message.from_user.first_name} ({user_id})"
            
            # Check rate limit
            if not self._check_rate_limit(user_id):
                self.logger.warning(f"Rate limit exceeded for {user_info}")
                self._send_rate_limit_message(message.chat.id)
                return
            
            # Extract phone number from command
            command_parts = message.text.split()
            if len(command_parts) < 2:
                self.bot.send_message(
                    message.chat.id,
                    "❌ Please provide a phone number.\n\nExample: `/lookup +1234567890`",
                    parse_mode='Markdown'
                )
                return
            
            phone_number = command_parts[1]
            self._perform_lookup(message.chat.id, phone_number, user_info)
            
        except Exception as e:
            self.logger.error(f"Error in handle_lookup: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ An error occurred while processing your lookup request."
            )
    
    def handle_status(self, message):
        """Handle /status command."""
        try:
            user_info = f"User: {message.from_user.first_name} ({message.from_user.id})"
            self.logger.info(f"Status command received from {user_info}")
            
            # Send "checking..." message
            status_msg = self.bot.send_message(
                message.chat.id,
                "🔍 Checking system status..."
            )
            
            # Check API status
            api_status = self.api.check_api_status()
            
            status_text = f"""
📊 **System Status**

🤖 **Bot Status:** ✅ Online
⚡ **API Status:** {'✅ Online' if api_status else '❌ Offline'}
🕐 **Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 **Rate Limits:**
• Max requests: {self.config.RATE_LIMIT_REQUESTS} per {self.config.RATE_LIMIT_WINDOW}s
• API timeout: {self.config.API_TIMEOUT}s

🔧 **Configuration:**
• API Endpoint: {self.config.PIRATE_OSINT_BASE_URL}
• Log Level: {self.config.LOG_LEVEL}
            """
            
            # Update the status message
            self.bot.edit_message_text(
                status_text,
                message.chat.id,
                status_msg.message_id,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in handle_status: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ Unable to retrieve system status."
            )
    
    def handle_text_message(self, message):
        """Handle regular text messages (for phone number lookups)."""
        try:
            user_id = message.from_user.id
            user_info = f"User: {message.from_user.first_name} ({user_id})"
            text = message.text.strip()
            
            # Skip if message is a command
            if text.startswith('/'):
                return
            
            # Check if it looks like a phone number
            if is_valid_phone_number(text):
                # Check rate limit
                if not self._check_rate_limit(user_id):
                    self.logger.warning(f"Rate limit exceeded for {user_info}")
                    self._send_rate_limit_message(message.chat.id)
                    return
                
                self._perform_lookup(message.chat.id, text, user_info)
            else:
                # Send help message for invalid input
                self.bot.send_message(
                    message.chat.id,
                    "❓ I didn't understand that. Please send a phone number or use /help for more information."
                )
        
        except Exception as e:
            self.logger.error(f"Error in handle_text_message: {e}")
    
    def _perform_lookup(self, chat_id: int, phone_number: str, user_info: str):
        """Perform OSINT lookup on phone number."""
        try:
            # Format and validate phone number
            formatted_number = format_phone_number(phone_number)
            
            self.logger.info(f"Lookup request for {formatted_number} from {user_info}")
            
            # Send "searching..." message
            search_msg = self.bot.send_message(
                chat_id,
                f"🔍 Searching for information about `{escape_markdown(formatted_number)}`...",
                parse_mode='Markdown'
            )
            
            # Perform API lookup
            result = self.api.lookup_number(formatted_number)
            
            if result['success']:
                # Format successful result
                response = self._format_lookup_result(formatted_number, result['data'])
                
                # Add back to menu button to results
                markup = types.InlineKeyboardMarkup()
                search_again_btn = types.InlineKeyboardButton("🔍 Search Another", callback_data="lookup")
                menu_btn = types.InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")
                markup.add(search_again_btn, menu_btn)
                
                # Update the search message with results
                self.bot.edit_message_text(
                    response,
                    chat_id,
                    search_msg.message_id,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
                
                self.logger.info(f"Successful lookup for {formatted_number} from {user_info}")
                
            else:
                # Handle API error
                error_msg = f"❌ Lookup failed: {result['error']}"
                
                self.bot.edit_message_text(
                    error_msg,
                    chat_id,
                    search_msg.message_id
                )
                
                self.logger.warning(f"Failed lookup for {formatted_number} from {user_info}: {result['error']}")
        
        except Exception as e:
            self.logger.error(f"Error in _perform_lookup: {e}")
            try:
                self.bot.send_message(
                    chat_id,
                    "❌ An error occurred during the lookup. Please try again later."
                )
            except:
                pass
    
    def _format_lookup_result(self, phone_number: str, data: Dict) -> str:
        """Format the lookup result for display."""
        try:
            if not data:
                return f"""
🔍 **OSINT Lookup Results**

📱 **Number:** `{escape_markdown(phone_number)}`
📊 **Status:** No information found
🕐 **Searched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ℹ️ This number may be private or not in our database.
                """
            
            # Handle list format from API
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Take the first result
            
            # If still no data after extraction
            if not data or not isinstance(data, dict):
                return f"""
🔍 **OSINT Lookup Results**

📱 **Number:** `{escape_markdown(phone_number)}`
📊 **Status:** No valid information found
🕐 **Searched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ℹ️ This number may be private or not in our database.
                """
            
            # Build formatted result message
            result_lines = [
                "🔍 **OSINT Lookup Results**",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📱 **Number:** `{escape_markdown(phone_number)}`",
                f"✅ **Status:** Information Found",
                "",
            ]
            
            # Format person details
            if data.get('name'):
                result_lines.append(f"👤 **Name:** {escape_markdown(data['name'])}")
            
            if data.get('father_name'):
                result_lines.append(f"👨 **Father's Name:** {escape_markdown(data['father_name'])}")
            
            # Format contact information
            if data.get('mobile') and data['mobile'] != phone_number:
                result_lines.append(f"📞 **Primary Mobile:** `{escape_markdown(data['mobile'])}`")
            
            if data.get('alt_mobile'):
                result_lines.append(f"📱 **Alternative Mobile:** `{escape_markdown(data['alt_mobile'])}`")
            
            if data.get('email') and data['email'].strip():
                result_lines.append(f"📧 **Email:** {escape_markdown(data['email'])}")
            
            # Format address with proper cleaning
            if data.get('address'):
                # Clean up address formatting - remove ! separators and fix formatting
                address = data['address'].replace('!', ' ').replace('  ', ' ').strip()
                # Split and rejoin to clean up spacing
                address_parts = [part.strip() for part in address.split() if part.strip()]
                clean_address = ' '.join(address_parts)
                result_lines.extend([
                    "",
                    f"🏠 **Address:**",
                    f"   {escape_markdown(clean_address)}"
                ])
            
            # Format network information
            if data.get('circle'):
                result_lines.append(f"🌐 **Network Circle:** {escape_markdown(data['circle'])}")
            
            # Format ID information
            if data.get('id_number'):
                result_lines.append(f"🆔 **ID Number:** `{escape_markdown(str(data['id_number']))}`")
            
            if data.get('id'):
                result_lines.append(f"🔢 **Database ID:** `{escape_markdown(str(data['id']))}`")
            
            # Add timestamp and disclaimer
            result_lines.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                f"🕐 **Search Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "⚠️ **Disclaimer:** Use this information responsibly and in accordance with local laws.",
                "🔒 This data is sourced from publicly available information."
            ])
            
            return "\n".join(result_lines)
        
        except Exception as e:
            self.logger.error(f"Error formatting lookup result: {e}")
            return f"""
🔍 **OSINT Lookup Results**

📱 **Number:** `{escape_markdown(phone_number)}`
❌ **Status:** Error formatting results
🕐 **Searched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Raw data available but couldn't be formatted properly.
            """
    
    def handle_callback_query(self, call):
        """Handle inline keyboard button presses."""
        try:
            user_info = f"User: {call.from_user.first_name} ({call.from_user.id})"
            self.logger.info(f"Callback query '{call.data}' from {user_info}")
            
            if call.data == "help":
                self._show_help_menu(call.message.chat.id, call.message.message_id)
            elif call.data == "status":
                self._show_status_info(call.message.chat.id, call.message.message_id)
            elif call.data == "lookup":
                self._show_lookup_instructions(call.message.chat.id, call.message.message_id)
            elif call.data == "examples":
                self._show_examples(call.message.chat.id, call.message.message_id)
            elif call.data == "back_main":
                self._show_main_menu(call.message.chat.id, call.message.message_id)
            
            # Answer the callback query
            self.bot.answer_callback_query(call.id)
            
        except Exception as e:
            self.logger.error(f"Error in handle_callback_query: {e}")
            try:
                self.bot.answer_callback_query(call.id, "❌ Error occurred")
            except:
                pass
    
    def _show_help_menu(self, chat_id, message_id):
        """Show help information with buttons."""
        help_text = """
📖 **Pirate OSINT Bot Help**

🔍 **Available Features:**
• **Phone Number Lookup** - Get detailed information about any phone number
• **Contact Details** - Name, address, alternative numbers
• **Network Information** - Carrier details and location
• **Fast & Secure** - Quick searches with privacy protection

📋 **How to Use:**
1️⃣ Click "🔍 Search Number" button
2️⃣ Send any phone number (with or without country code)
3️⃣ Get comprehensive OSINT results instantly

📞 **Supported Formats:**
• `+1234567890` (International)
• `1234567890` (National)
• `+1-234-567-8900` (With separators)

⚡ **Rate Limits:** {rate_limit} requests per {window} seconds
🔒 **Privacy:** No data stored, secure searches only
        """.format(rate_limit=self.config.RATE_LIMIT_REQUESTS, window=self.config.RATE_LIMIT_WINDOW)
        
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_main")
        lookup_btn = types.InlineKeyboardButton("🔍 Start Lookup", callback_data="lookup")
        markup.add(lookup_btn)
        markup.add(back_btn)
        
        self.bot.edit_message_text(
            help_text,
            chat_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    def _show_status_info(self, chat_id, message_id):
        """Show bot status with buttons."""
        # Check API status
        api_status = self.api.check_api_status()
        
        status_text = f"""
📊 **System Status Dashboard**

🤖 **Bot Status:** ✅ Online & Ready
⚡ **API Status:** {'✅ Online' if api_status else '❌ Offline'}
🕐 **Last Check:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 **Performance Metrics:**
• **Rate Limit:** {self.config.RATE_LIMIT_REQUESTS} requests per {self.config.RATE_LIMIT_WINDOW}s
• **API Timeout:** {self.config.API_TIMEOUT} seconds
• **Response Time:** {'< 2s' if api_status else 'N/A'}

🔧 **Configuration:**
• **API Endpoint:** pirate-osint.onrender.com
• **Log Level:** {self.config.LOG_LEVEL}
• **Security:** ✅ Enabled

🌍 **Service Regions:** Global Coverage
        """
        
        markup = types.InlineKeyboardMarkup()
        refresh_btn = types.InlineKeyboardButton("🔄 Refresh Status", callback_data="status")
        back_btn = types.InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_main")
        markup.add(refresh_btn)
        markup.add(back_btn)
        
        self.bot.edit_message_text(
            status_text,
            chat_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    def _show_lookup_instructions(self, chat_id, message_id):
        """Show lookup instructions with buttons."""
        instruction_text = """
🔍 **Phone Number Lookup**

📱 **Ready to search?** Simply send me any phone number and I'll gather intelligence information for you!

📋 **Instructions:**
1️⃣ Send the phone number in any format
2️⃣ Wait for results (usually takes 2-5 seconds)
3️⃣ Review the detailed OSINT report

💡 **Example Numbers to Try:**
• `+1234567890`
• `9876543210` 
• `+91-987-654-3210`

⚠️ **Important Notes:**
• Use only for legitimate purposes
• Respect privacy and local laws
• Rate limited for fair usage

🚀 **Ready?** Send any phone number now!
        """
        
        markup = types.InlineKeyboardMarkup()
        examples_btn = types.InlineKeyboardButton("💡 View Examples", callback_data="examples")
        back_btn = types.InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_main")
        markup.add(examples_btn)
        markup.add(back_btn)
        
        self.bot.edit_message_text(
            instruction_text,
            chat_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    def _show_examples(self, chat_id, message_id):
        """Show example usage with buttons."""
        examples_text = """
💡 **Usage Examples**

📱 **Valid Phone Number Formats:**

🇮🇳 **Indian Numbers:**
• `9876543210`
• `+91 9876543210`
• `+91-987-654-3210`

🇺🇸 **US Numbers:**
• `1234567890`
• `+1 234 567 8900`
• `(234) 567-8900`

🌍 **International:**
• `+44 7911 123456` (UK)
• `+86 138 0013 8000` (China)
• `+33 1 42 86 83 26` (France)

✅ **What You'll Get:**
• 👤 Full name and father's name
• 🏠 Complete address details
• 📞 Alternative phone numbers
• 🌐 Network carrier information
• 🆔 Associated ID numbers

🚀 **Try It:** Send any number now!
        """
        
        markup = types.InlineKeyboardMarkup()
        lookup_btn = types.InlineKeyboardButton("🔍 Start Lookup", callback_data="lookup")
        back_btn = types.InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_main")
        markup.add(lookup_btn)
        markup.add(back_btn)
        
        self.bot.edit_message_text(
            examples_text,
            chat_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
    
    def _show_main_menu(self, chat_id, message_id):
        """Show main menu."""
        welcome_text = """
🏴‍☠️ **Welcome to Pirate OSINT Bot!**

Your ultimate tool for OSINT phone number lookups and intelligence gathering.

🔍 **What can I do?**
• Phone number intelligence gathering
• Contact information lookup
• Address & network details
• Fast and secure searches

🚀 **Get Started:**
Choose an option below or simply send me a phone number!
        """
        
        # Create main menu with attractive buttons
        markup = types.InlineKeyboardMarkup(row_width=2)
        lookup_btn = types.InlineKeyboardButton("🔍 Search Number", callback_data="lookup")
        help_btn = types.InlineKeyboardButton("📖 Help", callback_data="help")
        status_btn = types.InlineKeyboardButton("📊 Bot Status", callback_data="status")
        examples_btn = types.InlineKeyboardButton("💡 Examples", callback_data="examples")
        markup.add(lookup_btn)
        markup.add(help_btn, status_btn)
        markup.add(examples_btn)
        
        self.bot.edit_message_text(
            welcome_text,
            chat_id,
            message_id,
            parse_mode='Markdown',
            reply_markup=markup
        )
