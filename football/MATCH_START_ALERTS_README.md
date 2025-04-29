# Football Match Start Alerts System

This README documents the match start alerts system and all alert types implemented for the football monitoring system.

## System Overview

The alerts system is designed to monitor live football matches and trigger notifications based on specific criteria. The system is built on top of the `live.py` script (which remains unchanged) and sends notifications through Telegram.

### Alert System Structure

```
football/
├── alerts/               # Main alerts directory
│   ├── __init__.py       # Package initialization
│   ├── base.py           # Base alert class (if created)
│   ├── ThreeHtZero.py    # 3HT0 alert (halftime 0-0 with high line)
│   ├── HighLineHalftimeZero.py  # High line alert class
│   └── match_start/      # Alerts for match beginning
│       ├── __init__.py   # Package initialization
│       └── three_ou.py   # 3 O/U Started alert
├── football_alerts.py    # Main alerts system script
├── live.py               # Core data fetching (unchanged)
└── [Other system files]  # Startup scripts, etc.
```

## Match Start Alerts

Match start alerts are designed to trigger in the early stages of a match when specific conditions are met. These alerts help identify betting opportunities right at the beginning of a game.

### 3 O/U Started Alert

**File:** `alerts/match_start/three_ou.py`  
**Class:** `ThreeOUStartAlert`

This alert triggers when a match in its early stages (first half, within the first ~10 minutes) has an Over/Under line of minimum 3.0 (measured at minutes 4-6).

#### Alert Criteria:
- Match is in first half (status_id = 2)
- Match is in early stages (within first 10 minutes)
- Over/Under line is greater than or equal to 3.0
- Line value is from minutes 4-6 of the match

#### Alert Format:
```
ALERT TYPE: 3 O/U Started
----- MATCH SUMMARY -----
Competition ID: [competition_id]
Competition: [competition_name]
Match: [home_team] vs [away_team]
Score: [home_score] - [away_score]
Status: First half (Minute: [match_minute], Status ID: [status_id])

--- MATCH BETTING ODDS ---
ML (Money Line):
Time: [time] min | Home: [home_odds] | Draw: [draw_odds] | Away: [away_odds]

SPREAD (Asia Handicap):
Time: [time] min | Home: [home_odds] | Handicap: [handicap] | Away: [away_odds]

Over/Under:
Time: [time] min | Over: [over_odds] | Line: [line_value] | Under: [under_odds]

--- MATCH ENVIRONMENT ---
Weather: [weather_description]
Wind: [wind_speed]
Humidity: [humidity_percentage]
```

## Halftime Alerts

Halftime alerts trigger when matches reach halftime and meet specific criteria.

### 3HT0 Alert

**File:** `alerts/ThreeHtZero.py`  
**Class:** `ThreeHtZeroAlert`

This alert triggers when a match with an Over/Under line of minimum 3.0 reaches halftime with a 0-0 score.

#### Alert Criteria:
- Match initially has an Over/Under line of minimum 3.0 (measured at minutes 4-6)
- Match reaches halftime (status_id = 3)
- Score is 0-0 at halftime

#### Alert Format:
Same as the 3 O/U Started alert, but with status showing half-time.

### HighLineHalftimeZero Alert

**File:** `alerts/HighLineHalftimeZero.py`  
**Class:** `HighLineHalftimeZeroAlert`

Another implementation of the halftime 0-0 alert with high expected goals.

## Using the Alerts System

### Running the System

The alerts system runs automatically in the background when you start the football monitoring system:

```bash
# Start/restart the entire system (both live.py and alerts)
bash /root/CascadeProjects/sports\ bot/football/restart_all.sh

# View live match data in your terminal
bash /root/CascadeProjects/sports\ bot/football/show_matches.sh

# View alert system logs
tail -f football/alerts.log
```

### System Configuration

- **Update Frequency:** Both the live match monitoring and alerts check for updates every 30 seconds
- **Telegram Integration:** Alerts are sent to your Telegram bot using the configured token and chat ID
- **Automatic Startup:** The system automatically restarts when the server boots via crontab

## Creating New Alerts

To create a new alert type:

1. Decide where it belongs (match_start, halftime, etc.)
2. Create a new Python file in the appropriate directory
3. Extend the `AlertCriteria` class
4. Implement the `check()` method with your criteria logic
5. Add your alert to `football_alerts.py` in the main function

### Example Alert Implementation

```python
class MyNewAlert(AlertCriteria):
    def __init__(self):
        super().__init__("My New Alert")
        self.tracked_matches = set()
    
    def check(self, match_data, home_team, away_team, competition_name):
        # Your logic here to determine if alert should trigger
        if [your_criteria_met] and match_id not in self.tracked_matches:
            self.tracked_matches.add(match_id)
            message = self.format_message(match_data, home_team, away_team, competition_name)
            return True, message
        return False, ""
```

## Extending the System

The alerts system is designed to be easily extended with new alert types. To add new categories of alerts:

1. Create a new directory under `alerts/` for your category
2. Add an `__init__.py` file to make it a proper package
3. Create your alert classes in Python files within the directory
4. Import and use your new alerts in `football_alerts.py`

## Troubleshooting

If alerts aren't triggering as expected:

1. Check the alerts log: `tail -f football/alerts.log`
2. Verify that the conditions you're checking for actually exist in the data
3. Ensure your alert class is properly imported and added to the AlertManager
4. Check the Telegram bot token and chat ID are correct

## Credits

This system integrates with TheSports API to fetch live match data and uses the Telegram Bot API for notifications.
