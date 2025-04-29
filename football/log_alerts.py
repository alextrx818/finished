#!/usr/bin/env python3
"""
Log Alerts System for Football Data
Scans log files for specific match criteria and sends alerts via Telegram
"""

import os
import re
import time
import datetime
import argparse
import logging
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/log_alerts.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("log_alerts")

# Configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
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

class ThreeHtZeroLoggerAlert(LogScannerAlert):
    """
    3HT0 (Logger) Alert
    Criteria:
    - Status: Half-time break (Status ID: 3)
    - Score: 0-0
    - Over/Under line: minimum 3.0, no maximum
    """
    def __init__(self, telegram_token=None, telegram_chat_id=None):
        super().__init__("3HT0 (Logger)", telegram_token, telegram_chat_id)
    
    def scan_log_file(self, log_file):
        """Scan the log file for matches meeting the 3HT0 criteria"""
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Split the log file into individual match blocks
        match_blocks = re.split(r'==================================================\nMATCH #\d+ OF \d+\n==================================================', content)
        
        # Process each match block
        for block in match_blocks:
            if not block.strip():
                continue
                
            # Create a match identifier
            match_id = None
            match_name = None
            competition = None
            
            # Check if this match is at half-time with 0-0 score
            is_halftime = "Status: Half-time break (Status ID: 3)" in block
            is_zero_zero = "Score: 0 - 0" in block
            
            # Extract Over/Under line
            ou_line = None
            ou_time = None
            if "Over/Under:" in block:
                ou_match = re.search(r'Over/Under:.*\nTime: (\d+) min \| Over: [+-]\d+ \| Line: (\d+\.?\d*) \| Under: [+-]\d+', block)
                if ou_match:
                    ou_time = int(ou_match.group(1))
                    ou_line = float(ou_match.group(2))
            
            # Extract match name and competition for identification
            match_name_match = re.search(r'Match: (.*?)\n', block)
            if match_name_match:
                match_name = match_name_match.group(1).strip()
                
            competition_match = re.search(r'Competition: (.*?)\n', block)
            if competition_match:
                competition = competition_match.group(1).strip()
                
            # Create a unique match identifier
            if match_name and competition:
                match_id = f"{competition} - {match_name}"
            
            # Check if this match meets all criteria
            if (is_halftime and is_zero_zero and ou_line is not None and ou_time is not None and
                ou_line >= 3.0 and ou_time >= 4 and ou_time <= 6 and
                match_id and match_id not in self.tracked_matches):
                
                logger.info(f"Found match meeting 3HT0 criteria: {match_id}, O/U line: {ou_line}, Time: {ou_time} min")
                
                # Extract the full match summary section for the alert
                match_summary = ""
                in_match_section = False
                
                for line in block.split('\n'):
                    if "----- MATCH SUMMARY -----" in line:
                        in_match_section = True
                        match_summary += line + "\n"
                    elif in_match_section and "---" in line and "MATCH" in line:
                        # End of match summary section
                        in_match_section = False
                        match_summary += "\n"
                    elif in_match_section:
                        match_summary += line + "\n"
                
                # Add the O/U line information
                ou_section = ""
                in_ou_section = False
                
                for line in block.split('\n'):
                    if "Over/Under:" in line:
                        in_ou_section = True
                        ou_section += line + "\n"
                    elif in_ou_section and line.strip() == "":
                        in_ou_section = False
                        break
                    elif in_ou_section:
                        ou_section += line + "\n"
                
                # Format the alert message
                message = f"ALERT TYPE: {self.name}\n\n{match_summary}\n{ou_section}"
                
                # Send the Telegram alert
                self.send_telegram_alert(message)
                
                # Add this match to tracked matches
                self.tracked_matches.add(match_id)

def scan_logs(alerts, specific_date=None):
    """Scan log files for alerts"""
    # Determine which log file to scan
    if specific_date:
        log_date = specific_date
    else:
        log_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
    log_file = os.path.join(LOG_DIR, f"football_fetches_{log_date}.log")
    
    if not os.path.exists(log_file):
        logger.error(f"Log file {log_file} not found.")
        return
        
    logger.info(f"Scanning log file: {log_file}")
    
    # Run each alert scanner on the log file
    for alert in alerts:
        try:
            alert.scan_log_file(log_file)
        except Exception as e:
            logger.error(f"Error scanning with {alert.name}: {e}")

def continuous_scanning(alerts, interval=60):
    """Continuously scan logs for alerts at the specified interval"""
    logger.info(f"Starting continuous log scanning every {interval} seconds")
    
    try:
        while True:
            scan_logs(alerts)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Log scanning stopped by user.")
    except Exception as e:
        logger.error(f"Error in log scanning: {e}")

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Log Alerts System for Football Data')
    parser.add_argument('-c', '--continuous', action='store_true',
                        help='Run in continuous mode, scanning logs at regular intervals')
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Interval between scans in seconds (default: 60)')
    parser.add_argument('-d', '--date', type=str, default=None,
                        help='Specific date to scan logs for (YYYY-MM-DD, default: today)')
    parser.add_argument('-t', '--telegram-token', type=str, default=None,
                        help='Telegram bot token')
    parser.add_argument('-chat', '--telegram-chat-id', type=str, default=None,
                        help='Telegram chat ID')
    args = parser.parse_args()
    
    # Create alert instances
    alerts = [
        ThreeHtZeroLoggerAlert(args.telegram_token, args.telegram_chat_id)
    ]
    
    # Make sure logs directory exists
    os.makedirs(LOG_DIR, exist_ok=True)
    
    if args.continuous:
        continuous_scanning(alerts, args.interval)
    else:
        scan_logs(alerts, args.date)

if __name__ == "__main__":
    main()
