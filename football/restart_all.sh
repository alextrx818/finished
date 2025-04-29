#!/bin/bash
# Simple restart script for the football monitoring system

echo "Restarting Football Monitoring System..."

# Change to the project directory
cd "/root/CascadeProjects/sports bot"

# Stop any existing processes
echo "Stopping any existing processes..."
if [ -f football/running_pids.txt ]; then
  cat football/running_pids.txt | xargs kill 2>/dev/null || true
  echo "Existing processes stopped."
else
  echo "No PID file found. Checking for running processes..."
  pkill -f "football/live_monitor_wrapper.py" 2>/dev/null || true
  pkill -f "football/football_alerts.py" 2>/dev/null || true
fi

# Make sure processes are fully stopped before restarting
sleep 2

# Start everything again using the existing script
echo "Starting all services..."
bash football/start_24_7_monitoring.sh

echo "
=============================================
All services restarted successfully!
=============================================
"
