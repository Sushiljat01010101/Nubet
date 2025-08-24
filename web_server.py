#!/usr/bin/env python3
"""
Web Server for Pirate OSINT Telegram Bot
Runs bot + simple web server on port 5555 for Render.com deployment
"""

import os
import sys
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json

# Import bot modules
from main import main as run_bot
from config import Config

class BotStatusHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for bot status and health checks."""
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🏴‍☠️ Pirate OSINT Bot</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: rgba(0,0,0,0.3); 
            padding: 30px; 
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ text-align: center; margin-bottom: 30px; }}
        .status {{ 
            background: rgba(0,255,0,0.2); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0;
            border: 1px solid #00ff00;
        }}
        .feature {{ 
            background: rgba(255,255,255,0.1); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 10px 0; 
        }}
        .api-info {{ 
            background: rgba(255,165,0,0.2); 
            padding: 15px; 
            border-radius: 10px; 
            margin: 20px 0;
            border: 1px solid #ffa500;
        }}
        .footer {{ text-align: center; margin-top: 30px; color: #ccc; }}
        .emoji {{ font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏴‍☠️ Pirate OSINT Telegram Bot</h1>
        
        <div class="status">
            <h2>🟢 Status: ONLINE & READY</h2>
            <p><strong>Server Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p><strong>Port:</strong> 5555</p>
            <p><strong>Platform:</strong> Render.com</p>
        </div>

        <div class="api-info">
            <h3>🔗 API Configuration</h3>
            <p><strong>OSINT API:</strong> pirate-osint.onrender.com</p>
            <p><strong>Bot Status:</strong> ✅ Active and Listening</p>
            <p><strong>Rate Limiting:</strong> 5 requests per 60 seconds</p>
        </div>

        <h3>🚀 Bot Features</h3>
        <div class="feature">
            <span class="emoji">🔍</span> <strong>Phone Number OSINT Lookup</strong><br>
            Get detailed information about phone numbers including name, address, and network details.
        </div>
        
        <div class="feature">
            <span class="emoji">🎯</span> <strong>Interactive Button Interface</strong><br>
            Easy-to-use button navigation with professional UI design.
        </div>
        
        <div class="feature">
            <span class="emoji">📊</span> <strong>Real-time Status Monitoring</strong><br>
            Live system status with API health checks and performance metrics.
        </div>
        
        <div class="feature">
            <span class="emoji">🛡️</span> <strong>Rate Limiting & Security</strong><br>
            Built-in rate limiting and comprehensive error handling for stable operation.
        </div>

        <h3>📱 How to Use</h3>
        <div class="feature">
            <p>1. Find the bot on Telegram (search for your bot username)</p>
            <p>2. Send <code>/start</code> to begin</p>
            <p>3. Click "🔍 Search Number" or send any phone number</p>
            <p>4. Get comprehensive OSINT results instantly!</p>
        </div>

        <div class="footer">
            <p>🏴‍☠️ Pirate OSINT Bot | Powered by Python & Telegram Bot API</p>
            <p>Deployed on Render.com | Port 5555</p>
        </div>
    </div>
</body>
</html>
                """
                self.wfile.write(html_content.encode())
                
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "service": "pirate-osint-bot",
                    "port": 5555,
                    "bot_status": "running"
                }
                
                self.wfile.write(json.dumps(health_data).encode())
                
            elif self.path == '/api/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                config = Config()
                status_data = {
                    "bot_online": True,
                    "api_endpoint": config.PIRATE_OSINT_BASE_URL,
                    "rate_limit": config.RATE_LIMIT_REQUESTS,
                    "rate_window": config.RATE_LIMIT_WINDOW,
                    "timeout": config.API_TIMEOUT,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.wfile.write(json.dumps(status_data).encode())
                
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>404 - Page Not Found</h1><p>Go to <a href='/'>Home</a></p>")
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error: {str(e)}".encode())
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        logging.info(f"Web Server: {format % args}")

def run_web_server():
    """Run the web server on port 5555."""
    port = int(os.getenv('PORT', 5555))
    server = HTTPServer(('0.0.0.0', port), BotStatusHandler)
    logging.info(f"Web server starting on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Web server stopped")
        server.shutdown()

def main():
    """Main function to run both bot and web server."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Pirate OSINT Bot with Web Server")
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("Web server thread started")
    
    # Start the bot (this will block)
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()