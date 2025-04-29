#!/usr/bin/env python3
"""
Base Log Scanner Alert Class
Provides common functionality for all log-based alerts
"""

import os
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "logs/log_alerts.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("log_alerts")

# Default Telegram settings
DEFAULT_TELEGRAM_TOKEN = "5985601372:AAHDVArcK2W54K7r_YIq9GRQHVHVkXfh5Lw"
DEFAULT_TELEGRAM_CHAT_ID = "-1001982042886"

class LogScannerAlert:
    """Base class for log scanner alerts"""
    def __init__(self, name, telegram_token=None, telegram_chat_id=None):
        self.name = name
        self.telegram_token = telegram_token or DEFAULT_TELEGRAM_TOKEN
        self.telegram_chat_id = telegram_chat_id or DEFAULT_TELEGRAM_CHAT_ID
        self.tracked_matches = set()  # Keep track of matches we've already alerted on
        
    def scan_log_file(self, log_file):
        """Scan a log file for matches meeting the criteria"""
        raise NotImplementedError("Subclasses must implement this method")
        
    def send_telegram_alert(self, message):
        """Send an alert message via Telegram"""
        telegram_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        try:
            response = requests.post(
                telegram_url,
                json={
                    "chat_id": self.telegram_chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
            if response.status_code == 200:
                logger.info(f"Successfully sent Telegram alert for {self.name}")
            else:
                logger.error(f"Failed to send Telegram alert: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
