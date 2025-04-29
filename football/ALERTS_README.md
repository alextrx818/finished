# Football Alerts System

This system monitors live football matches and sends alerts through Telegram when specific criteria are met. It works alongside the main `live.py` script without modifying it.

## Features

- Sends alerts through Telegram messaging
- Multiple alert types for different match events
- Non-invasive design that respects the integrity of the core `live.py` script
- Customizable alert thresholds and criteria

## Alert Types

The system currently supports the following alert types:

1. **Goal Scored Alert**: Triggers when a goal is scored in any live match
2. **Half-Time Alert**: Notifies when a match reaches half-time
3. **Match End Alert**: Sends an alert when a match ends, including the final result
4. **High Odds Alert**: Triggers when betting odds exceed a specified threshold

## Setup Instructions

### Telegram Bot Setup

1. Create a Telegram bot using BotFather:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow the instructions
   - Save the bot token provided (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

2. Get your Chat ID:
   - Start a conversation with your bot
   - Send any message to the bot
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find the `chat` object and note the `id` value (this is your chat ID)

### Running the Alerts System

The script is already configured with your Telegram bot token and chat ID (6128359776). To run the alerts system, simply use:

```bash
python football/football_alerts.py
```

If you want to use a different chat ID, you can specify it as a parameter:

```bash
python football/football_alerts.py <DIFFERENT_CHAT_ID>
```

### Getting Your Chat ID

To get your chat ID:

1. Start a conversation with your bot by searching for `@FBBotAlerts_Bot` in Telegram
2. Click "Start" and send any message to the bot (like "hello")
3. Run this command to get your chat ID:
   ```bash
   curl -s "https://api.telegram.org/bot7764953908:AAHMpJsw5vKQYPiJGWrj0PgDkztiIgY_dko/getUpdates" | python3 -m json.tool
   ```
4. Look for the "chat" object in the response and note the "id" value - that's your chat ID

## Configuration

You can customize the alerts by modifying the following in the script:

- **Poll frequency**: Change the `time.sleep(60)` value to adjust how often the system checks for new alerts (currently set to 60 seconds)
- **High odds threshold**: Modify the `threshold=400` parameter when creating the `HighOddsAlert` to adjust the sensitivity
- **Add custom alerts**: Create new subclasses of `AlertCriteria` to implement your own alert conditions

## How It Works

The alert system:

1. Imports data from `live.py` without modifying it
2. Fetches live match data using the same API endpoints
3. Tracks the state of each match and compares with previous states
4. Triggers alerts when the defined conditions are met
5. Formats and sends alert messages through Telegram

## Alert Message Format

All alerts include:
- A descriptive emoji and title
- The teams involved and current score
- The competition name
- A timestamp of when the alert was triggered

## Implementation Details

### Code Structure

The alerts system is implemented in `football_alerts.py` and consists of:

1. **TelegramBot class**: Handles communication with the Telegram API
2. **AlertCriteria base class**: Defines the interface for all alert types
3. **Specific alert classes**:
   - `GoalScoredAlert`: Detects when goals are scored by comparing with previous scores
   - `HalfTimeAlert`: Checks for status_id changing to 3 (half-time)
   - `MatchEndAlert`: Monitors for status_id changing to 7 or 8 (finished)
   - `HighOddsAlert`: Analyzes betting odds for values above the threshold
4. **AlertManager class**: Coordinates checking all criteria against all live matches
5. **Main function**: Sets up the system and runs the monitoring loop

### Integration with live.py

The alerts system imports and uses functions from `live.py` without modifying the original file, preserving its integrity as the core of the project.

### Monitoring Frequency

The system checks for new alerts every 60 seconds by default, which can be adjusted in the main loop's `time.sleep()` call.

## Deployment Considerations

For running the system continuously (like on a server), consider:

1. Using a service manager like systemd to keep it running
2. Setting up log rotation for the output
3. Configuring it to start automatically after reboots

Example systemd service file (`/etc/systemd/system/football-alerts.service`):
```
[Unit]
Description=Football Alerts Telegram Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/football/football_alerts.py
WorkingDirectory=/path/to/project
Restart=always
User=yourusername

[Install]
WantedBy=multi-user.target
```

## Adding New Alert Types

To add a new alert type:

1. Create a new class that inherits from `AlertCriteria`
2. Implement the `check()` method that returns a tuple of (triggered, message)
3. Add your new criteria to the `AlertManager` in the `main()` function

Example:
```python
class MyNewAlert(AlertCriteria):
    def __init__(self):
        super().__init__("My Alert Name")
        
    def check(self, match_data, home_team, away_team, competition_name):
        match_id = match_data.get('id')
        
        # Your alert logic here
        should_trigger = False  # Replace with your condition
        
        if should_trigger and match_id not in self.triggered_matches:
            self.triggered_matches.add(match_id)
            return True, f"🔔 <b>MY ALERT!</b>\n\n" \
                   f"<b>{home_team} vs {away_team}</b>\n" \
                   f"Competition: {competition_name}\n" \
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        return False, ""
```

## Last Updated
2025-04-29
