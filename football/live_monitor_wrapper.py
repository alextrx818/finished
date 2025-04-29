#!/usr/bin/env python3
"""
Wrapper script for live.py that adds Telegram notifications for start/stop events
"""

import sys
import os
import time
import subprocess
import signal
from datetime import datetime
import requests

# Telegram configuration
TELEGRAM_TOKEN = "7764953908:AAHMpJsw5vKQYPiJGWrj0PgDkztiIgY_dko"
TELEGRAM_CHAT_ID = "6128359776"  # Default chat ID, should be overridden

class TelegramNotifier:
    """Simple Telegram notification class"""
    
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    def send_message(self, message):
        """Send message to Telegram"""
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(self.api_url, data=data)
            if response.status_code != 200:
                print(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM signals to send stop notification"""
    stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\nLive monitor stopped at {stop_time}")
    
    notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    stop_message = f"⏹️ <b>Football Live Monitor Stopped</b>\n" \
                  f"Time: {stop_time}\n" \
                  f"System was manually stopped."
    notifier.send_message(stop_message)
    
    sys.exit(0)

def main():
    # Parse arguments
    if len(sys.argv) >= 2:
        TELEGRAM_CHAT_ID = sys.argv[1]
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Send startup notification
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Starting Football Live Monitor at {start_time}")
    
    notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    start_message = f"▶️ <b>Football Live Monitor Started</b>\n" \
                    f"Time: {start_time}\n" \
                    f"Monitoring live matches 24/7."
    notifier.send_message(start_message)
    
    # Build the command to run live.py in continuous mode
    script_dir = os.path.dirname(os.path.abspath(__file__))
    live_script = os.path.join(script_dir, "live.py")
    
    # Run live.py in continuous mode
    cmd = [sys.executable, live_script, "--continuous"]
    if len(sys.argv) > 2:
        cmd.extend(["--interval", sys.argv[2]])
    
    try:
        # Run the live.py script and redirect output
        process = subprocess.Popen(cmd)
        process.wait()
    except Exception as e:
        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"Error in live monitor: {e}"
        print(error_msg)
        
        # Send error notification
        error_message = f"❌ <b>Football Live Monitor Error</b>\n" \
                       f"Time: {error_time}\n" \
                       f"Error: {error_msg}"
        notifier.send_message(error_message)
    
    # If we reach here, the process has ended
    if process.returncode != 0:
        stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        notifier.send_message(f"⚠️ <b>Football Live Monitor Exited</b>\n" \
                             f"Time: {stop_time}\n" \
                             f"Exit code: {process.returncode}")

if __name__ == "__main__":
    main()
