# Football Monitoring System - Startup Guide

This document explains how to run the 24/7 Football Monitoring System with Telegram notifications for start/stop events.

## System Components

The monitoring system consists of two main components:

1. **Live Football Monitor** (`live.py`):
   - Runs in continuous mode, fetching data every 30 seconds
   - Provides detailed match information (scores, odds, environment)
   - Now wrapped in `live_monitor_wrapper.py` to send Telegram start/stop notifications

2. **Football Alerts System** (`football_alerts.py`):
   - Monitors live matches for specific events
   - Sends Telegram alerts for goals, half-time, match end, and high odds
   - Now includes start/stop notification functionality

## Starting the System

### One-Click Startup

The simplest way to start everything is using the provided restart script:

```bash
# From any directory
/root/CascadeProjects/sports\ bot/football/restart_all.sh
```

This script:
- Stops any running instances
- Starts both the Live Monitor and Alerts System
- Redirects output to log files
- Sends Telegram notifications when services start

### Automatic Startup on Boot

The system is configured to start automatically when the server boots up via crontab.
This is already set up and working. No further action required.

To verify the crontab setup:
```bash
crontab -l
```

You should see:
```
@reboot /root/CascadeProjects/sports\ bot/football/restart_all.sh > /root/CascadeProjects/sports\ bot/football/cron.log 2>&1
```

## Monitoring and Management

### Checking Service Status

To check if the services are running:
```bash
ps aux | grep "football/live_monitor_wrapper.py\|football/football_alerts.py"
```

### Viewing Logs

Monitor the output of both services:
```bash
# Live Monitor logs
tail -f /root/CascadeProjects/sports\ bot/football/live_monitor.log

# Alerts System logs
tail -f /root/CascadeProjects/sports\ bot/football/alerts.log

# Startup log (from crontab)
tail -f /root/CascadeProjects/sports\ bot/football/cron.log
```

### Stopping Services

To stop all services:
```bash
# If you know the PIDs (stored in running_pids.txt)
cat /root/CascadeProjects/sports\ bot/football/running_pids.txt | xargs kill

# Or stop by name
pkill -f "football/live_monitor_wrapper.py"
pkill -f "football/football_alerts.py"
```

## Telegram Notifications

The system now sends Telegram notifications in these scenarios:

1. **Startup Events**:
   - When the Live Monitor starts
   - When the Alerts System starts
   - After system boot (automatic restart)

2. **Shutdown Events**:
   - When the Live Monitor stops (manual or crash)
   - When the Alerts System stops (manual or crash)

3. **Error Events**:
   - If either system encounters an error

All notifications include timestamps and relevant details.

## Customization

### Changing Update Interval

To modify how often the live monitor fetches new data:
1. Edit the `run_live_monitor.sh` script
2. Change the last parameter (default: 30 seconds)

### Modifying Alert Criteria

To adjust alert thresholds or add new alert types:
1. Edit `football_alerts.py`
2. Modify the existing criteria or add new ones to the `main()` function

### Changing Telegram Bot/Chat

To use a different Telegram bot or chat ID:
1. Edit both wrapper scripts to update the token/chat ID
2. Restart the services using the restart script

## Technical Details

- **Core Script**: `live.py` (unchanged as per your requirement)
- **Wrapper Script**: `live_monitor_wrapper.py` (adds Telegram notifications)
- **Alerts Script**: `football_alerts.py` (enhanced with start/stop notifications)
- **Startup Scripts**: 
  - `run_live_monitor.sh` (runs the live monitor)
  - `run_alerts.sh` (runs the alerts system)
  - `start_24_7_monitoring.sh` (starts both in background)
  - `restart_all.sh` (stops and restarts everything)

## Troubleshooting

### Services Not Starting

1. Check the log files for errors:
   ```bash
   cat /root/CascadeProjects/sports\ bot/football/cron.log
   cat /root/CascadeProjects/sports\ bot/football/live_monitor.log
   cat /root/CascadeProjects/sports\ bot/football/alerts.log
   ```

2. Try running the scripts directly to see error messages:
   ```bash
   cd /root/CascadeProjects/sports\ bot
   python3 football/live_monitor_wrapper.py
   python3 football/football_alerts.py
   ```

### No Telegram Notifications

1. Verify the bot token and chat ID in both scripts
2. Check internet connectivity
3. Confirm the Telegram bot is active
