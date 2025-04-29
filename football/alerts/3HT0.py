#!/usr/bin/env python3
"""
3HT0 Alert Criteria
Alert when matches with Over/Under line of 3.0+ reach halftime with 0-0 score
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from football_alerts import AlertCriteria
from football import live

class ThreeHtZeroAlert(AlertCriteria):
    """
    3HT0 Alert Criteria
    Tracks matches with Over/Under lines of 3.0+ at minutes 4-6
    Alerts when they reach halftime (status_id = 3) with 0-0 score
    """
    def __init__(self):
        super().__init__("3HT0")
        self.high_line_matches = {}  # Match ID -> Over/Under line value
        self.match_odds = {}         # Store full odds data for matches
        self.previous_status = {}    # Track previous match status
        
    def check(self, match_data, home_team, away_team, competition_name):
        """
        Check if the match meets the 3HT0 criteria:
        - Has Over/Under line >= 3.0 at minutes 4-6
        - Is at halftime (status_id = 3)
        - Score is 0-0
        
        Args:
            match_data (dict): Match data from the API
            home_team (str): Name of the home team
            away_team (str): Name of the away team
            competition_name (str): Name of the competition
            
        Returns:
            tuple: (bool, str) - Whether the alert was triggered and the alert message
        """
        match_id = match_data.get('id')
        if not match_id:
            return False, ""
            
        # Get current match status and score
        status_id = match_data.get('status_id')
        home_score = match_data.get('home_score', 0)
        away_score = match_data.get('away_score', 0)
        
        # Get previous status, default to None if not seen before
        previous_status = self.previous_status.get(match_id)
        
        # Update stored status for next check
        self.previous_status[match_id] = status_id
        
        # If match not already tracked as high line, check the odds
        if match_id not in self.high_line_matches:
            try:
                # Fetch and analyze odds data
                odds_data = live.fetch_match_odds(match_id)
                formatted_odds = live.format_match_odds(odds_data)
                
                # Look for Over/Under entries at minutes 4-6
                if "Over/Under" in formatted_odds and formatted_odds["Over/Under"]:
                    for entry in formatted_odds["Over/Under"]:
                        # Get the line value (points total)
                        if "line" in entry:
                            line_value = float(entry["line"])
                            time_match = entry.get("time_of_match", "")
                            
                            # Check if line is 3.0 or higher and from minutes 4-6
                            if line_value >= 3.0 and time_match.isdigit():
                                minute = int(time_match)
                                if 4 <= minute <= 6:
                                    # Store the line value and odds for this match
                                    self.high_line_matches[match_id] = line_value
                                    self.match_odds[match_id] = formatted_odds
                                    
                                    match_details = live.fetch_match_details(match_id)
                                    full_match_data = match_data.copy()
                                    if match_details and "results" in match_details:
                                        if isinstance(match_details["results"], list) and match_details["results"]:
                                            full_match_data.update(match_details["results"][0])
                                        elif isinstance(match_details["results"], dict):
                                            full_match_data.update(match_details["results"])
                                    
                                    # Store extra environment data for the alert
                                    self.match_odds[match_id]["environment"] = {
                                        "weather": full_match_data.get("weather_code", ""),
                                        "wind": full_match_data.get("wind", ""),
                                        "humidity": full_match_data.get("humidity", "")
                                    }
                                    self.match_odds[match_id]["competition_id"] = match_data.get("competition_id", "")
                                    
                                    print(f"Match {match_id} ({home_team} vs {away_team}) tracked for 3HT0 with high line {line_value}")
                                    break
            except Exception as e:
                print(f"Error checking odds for match {match_id}: {e}")
        
        # Check if this is a tracked match that just reached halftime with 0-0 score
        is_halftime = status_id == 3  # Status 3 = Half-time break
        is_scoreless = home_score == 0 and away_score == 0
        just_changed = previous_status is not None and previous_status != status_id
        is_high_line = match_id in self.high_line_matches
        
        if is_halftime and is_scoreless and just_changed and is_high_line and match_id not in self.triggered_matches:
            # Add to triggered matches to prevent duplicate alerts
            self.triggered_matches.add(match_id)
            
            # Format odds display in the exact format requested
            odds_message = self.format_odds_display(match_id, match_data)
            
            # Format environment data display
            env_message = self.format_environment_display(match_id)
            
            # Create the detailed alert message in the exact format requested
            message = (f"ALERT TYPE: 3HT0\n"
                       f"----- MATCH SUMMARY -----\n"
                       f"Competition ID: {self.match_odds[match_id].get('competition_id', 'Unknown')}\n"
                       f"Competition: {competition_name}\n"
                       f"Match: {home_team} vs {away_team}\n"
                       f"Score: {home_score} - {away_score} (HT: {home_score} - {away_score})\n"
                       f"Status: Half-time (Status ID: {status_id})\n\n"
                       f"{odds_message}\n\n"
                       f"{env_message}")
            
            return True, message
            
        # Remove from triggered matches once the match leaves halftime
        # This allows for new alerts if the match somehow returns to halftime
        elif not is_halftime and match_id in self.triggered_matches:
            self.triggered_matches.remove(match_id)
            
        return False, ""
    
    def format_odds_display(self, match_id, match_data):
        """Format the odds data for display in the alert message"""
        odds_data = self.match_odds.get(match_id, {})
        
        # Format the three sections of betting odds
        ml_section = "ML (Money Line):\nNo odds data available"
        spread_section = "SPREAD (Asia Handicap):\nNo odds data available"
        ou_section = "Over/Under:\nNo odds data available"
        
        # Format ML (Money Line) section
        if "ML" in odds_data and odds_data["ML"]:
            entry = odds_data["ML"][0]
            time_str = entry.get("time_of_match", "?")
            home_win = entry.get("home_win", "?")
            draw = entry.get("draw", "?")
            away_win = entry.get("away_win", "?")
            
            ml_section = f"ML (Money Line):\nTime: {time_str} min | Home: {live.format_american_odds(home_win)} | Draw: {live.format_american_odds(draw)} | Away: {live.format_american_odds(away_win)}"
        
        # Format SPREAD (Asia Handicap) section
        if "SPREAD" in odds_data and odds_data["SPREAD"]:
            entry = odds_data["SPREAD"][0]
            time_str = entry.get("time_of_match", "?")
            home_win = entry.get("home_win", "?")
            handicap = entry.get("handicap", "?")
            away_win = entry.get("away_win", "?")
            
            spread_section = f"SPREAD (Asia Handicap):\nTime: {time_str} min | Home: {live.format_american_odds(home_win)} | Handicap: {handicap} | Away: {live.format_american_odds(away_win)}"
        
        # Format Over/Under section
        if "Over/Under" in odds_data and odds_data["Over/Under"]:
            entry = odds_data["Over/Under"][0]
            time_str = entry.get("time_of_match", "?")
            over = entry.get("over", "?")
            line = entry.get("line", "?")
            under = entry.get("under", "?")
            
            ou_section = f"Over/Under:\nTime: {time_str} min | Over: {live.format_american_odds(over)} | Line: {line} | Under: {live.format_american_odds(under)}"
        
        return f"--- MATCH BETTING ODDS ---\n{ml_section}\n\n{spread_section}\n\n{ou_section}"
    
    def format_environment_display(self, match_id):
        """Format the environment data for display in the alert message"""
        odds_data = self.match_odds.get(match_id, {})
        environment = odds_data.get("environment", {})
        
        # Get environment data
        weather_code = environment.get("weather", "")
        wind = environment.get("wind", "")
        humidity = environment.get("humidity", "")
        
        # Format the weather description
        weather_desc = live.get_weather_description(weather_code) if weather_code else "Unknown"
        
        # Format wind if available
        wind_text = wind if wind else "Unknown"
        if "m/s" not in wind_text and wind_text != "Unknown":
            wind_text = f"{wind_text}m/s"
        
        # Format humidity if available
        humidity_text = humidity if humidity else "Unknown"
        if "%" not in humidity_text and humidity_text != "Unknown":
            humidity_text = f"{humidity_text}%"
        
        return f"--- MATCH ENVIRONMENT ---\nWeather: {weather_desc}\nWind: {wind_text}\nHumidity: {humidity_text}"
