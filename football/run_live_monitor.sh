#!/bin/bash
# Script to run the live monitor wrapper in continuous mode

echo "Starting Football Live Monitor with Telegram notifications..."
echo "Press Ctrl+C to stop"
echo "Started at: $(date)"
echo "========================================"

# Run the wrapper script which will send Telegram notifications and then run live.py
cd "/root/CascadeProjects/sports bot"
python3 football/live_monitor_wrapper.py 6128359776 30
