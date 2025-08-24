#!/bin/bash
# Render.com startup script for Pirate OSINT Bot

echo "Installing dependencies..."
pip install pyTelegramBotAPI==4.28.0 requests==2.32.5 python-dotenv==1.1.1

echo "Starting Pirate OSINT Bot with Web Server..."
python web_server.py