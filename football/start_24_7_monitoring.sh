#!/bin/bash
# Script to start both the Live Monitor and Alerts system as background processes

cd "/root/CascadeProjects/sports bot"

echo "Starting Football Live Monitor in the background..."
nohup bash football/run_live_monitor.sh > football/live_monitor.log 2>&1 &
LIVE_PID=$!
echo "Live Monitor started with PID: $LIVE_PID"
echo "Live Monitor logs: football/live_monitor.log"

echo ""
echo "Starting Football Alerts System in the background..."
nohup bash football/run_alerts.sh > football/alerts.log 2>&1 &
ALERTS_PID=$!
echo "Alerts System started with PID: $ALERTS_PID"
echo "Alerts logs: football/alerts.log"

echo ""
echo "Both systems are now running in the background."
echo "To view the logs:"
echo "  tail -f football/live_monitor.log"
echo "  tail -f football/alerts.log"
echo ""
echo "To stop the processes:"
echo "  kill $LIVE_PID $ALERTS_PID"
echo ""
echo "To automatically start these services on boot, add this line to your crontab:"
echo "  @reboot cd $(pwd) && bash football/start_24_7_monitoring.sh"
echo ""
echo "To edit your crontab:"
echo "  crontab -e"

# Save the PIDs to a file for easy reference later
echo "$LIVE_PID $ALERTS_PID" > football/running_pids.txt
echo "PIDs saved to football/running_pids.txt"
