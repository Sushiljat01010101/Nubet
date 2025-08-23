"""
Pirate OSINT API integration module.
"""

import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from config import Config
from utils import format_phone_number

class PirateOSINTAPI:
    """Interface for the Pirate OSINT API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Set session timeout
        self.session.timeout = config.API_TIMEOUT
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'Pirate-OSINT-Telegram-Bot/1.0'
        })
    
    def lookup_number(self, phone_number: str) -> Dict[str, Any]:
        """
        Perform OSINT lookup on a phone number.
        
        Args:
            phone_number: Phone number to lookup
            
        Returns:
            Dict containing success status and data/error
        """
        try:
            # Format phone number
            formatted_number = format_phone_number(phone_number)
            
            # Build API URL
            params = {
                'key': self.config.PIRATE_OSINT_API_KEY,
                'num': formatted_number
            }
            
            url = f"{self.config.PIRATE_OSINT_BASE_URL}?{urlencode(params)}"
            
            self.logger.info(f"Making API request for number: {formatted_number}")
            
            # Make API request
            response = self.session.get(
                url,
                timeout=self.config.API_TIMEOUT
            )
            
            # Log response status
            self.logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'success': True,
                        'data': data,
                        'status_code': response.status_code
                    }
                except ValueError as e:
                    # Handle non-JSON responses
                    self.logger.warning(f"Non-JSON response received: {e}")
                    return {
                        'success': True,
                        'data': {'response': response.text},
                        'status_code': response.status_code
                    }
            
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Number not found in database',
                    'status_code': response.status_code
                }
            
            elif response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Invalid API key',
                    'status_code': response.status_code
                }
            
            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': 'API rate limit exceeded. Please try again later.',
                    'status_code': response.status_code
                }
            
            else:
                return {
                    'success': False,
                    'error': f'API returned status code {response.status_code}',
                    'status_code': response.status_code
                }
        
        except requests.exceptions.Timeout:
            self.logger.error("API request timeout")
            return {
                'success': False,
                'error': 'Request timeout. The API is taking too long to respond.'
            }
        
        except requests.exceptions.ConnectionError:
            self.logger.error("API connection error")
            return {
                'success': False,
                'error': 'Unable to connect to the API. Please try again later.'
            }
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return {
                'success': False,
                'error': 'Network error occurred while contacting the API.'
            }
        
        except Exception as e:
            self.logger.error(f"Unexpected error in lookup_number: {e}")
            return {
                'success': False,
                'error': 'An unexpected error occurred during the lookup.'
            }
    
    def check_api_status(self) -> bool:
        """
        Check if the API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Make a simple request to check API availability
            params = {
                'key': self.config.PIRATE_OSINT_API_KEY,
                'num': '1234567890'  # Test number
            }
            
            url = f"{self.config.PIRATE_OSINT_BASE_URL}?{urlencode(params)}"
            
            response = self.session.get(
                url,
                timeout=10  # Short timeout for status check
            )
            
            # Consider API available if we get any response (even errors)
            return response.status_code in [200, 404, 401, 429]
        
        except Exception as e:
            self.logger.error(f"API status check failed: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and configuration.
        
        Returns:
            Dictionary with API information
        """
        return {
            'base_url': self.config.PIRATE_OSINT_BASE_URL,
            'has_api_key': bool(self.config.PIRATE_OSINT_API_KEY),
            'timeout': self.config.API_TIMEOUT,
            'status': 'configured' if self.config.PIRATE_OSINT_API_KEY else 'not_configured'
        }
