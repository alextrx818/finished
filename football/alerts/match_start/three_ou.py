#!/usr/bin/env python3
"""
3 O/U Started Alert
Alerts when a match starts and has an Over/Under line of minimum 3.0 at minutes 4-6
"""

import sys
import os
from datetime import datetime

# Add parent directories to path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from football_alerts import AlertCriteria
from football import live

class ThreeOUStartAlert(AlertCriteria):
    """
    3 O/U Started Alert
    
    Alerts when:
    1. A match is in its early stages (minutes 4-6 of play)
    2. The Over/Under line is minimum 3.0
    """
    
    def __init__(self):
        super().__init__("3 O/U Started")
        self.tracked_matches = set()  # Track which matches we've already alerted for
        
    def check(self, match_data, home_team, away_team, competition_name):
        """
        Check if the match meets the criteria:
        - Match is in early stages (first half, within first ~10 minutes)
        - Has Over/Under line >= 3.0 at minutes 4-6
        
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
            
        # Skip if we've already alerted for this match
        if match_id in self.tracked_matches:
            return False, ""
            
        # Check if match is in first half
        status_id = match_data.get('status_id')
        is_first_half = status_id == 2  # Status 2 = First half
        
        # Check if match is in early stages (using match_minute if available)
        match_minute = match_data.get('match_minute', 0)
        try:
            minute = int(match_minute) if match_minute else 0
        except (ValueError, TypeError):
            minute = 0
            
        is_early_match = minute <= 10  # Consider first 10 minutes as early match
        
        # Only proceed if match is in first half and in early stages
        if not (is_first_half and is_early_match):
            return False, ""
            
        # Check the odds data to see if O/U line is minimum 3.0
        try:
            # Fetch and analyze odds data
            odds_data = live.fetch_match_odds(match_id)
            formatted_odds = live.format_match_odds(odds_data)
            
            # Look for Over/Under entries at minutes 4-6
            high_line_found = False
            line_value = 0
            time_str = ""
            over_odds = ""
            under_odds = ""
            
            if "Over/Under" in formatted_odds and formatted_odds["Over/Under"]:
                for entry in formatted_odds["Over/Under"]:
                    # Get the line value (points total)
                    if "line" in entry:
                        current_line = float(entry["line"])
                        current_time = entry.get("time_of_match", "")
                        
                        # Check if line is 3.0 or higher and from minutes 4-6
                        if current_line >= 3.0 and current_time.isdigit():
                            minute = int(current_time)
                            if 4 <= minute <= 6:
                                high_line_found = True
                                line_value = current_line
                                time_str = current_time
                                over_odds = entry.get("over", "?")
                                under_odds = entry.get("under", "?")
                                break
            
            # If we found a high line, trigger the alert
            if high_line_found:
                # Add to tracked matches to prevent duplicate alerts
                self.tracked_matches.add(match_id)
                
                # Get match details
                match_details = live.fetch_match_details(match_id)
                full_match_data = match_data.copy()
                if match_details and "results" in match_details:
                    if isinstance(match_details["results"], list) and match_details["results"]:
                        full_match_data.update(match_details["results"][0])
                    elif isinstance(match_details["results"], dict):
                        full_match_data.update(match_details["results"])
                
                # Format odds display
                odds_message = self.format_odds_display(formatted_odds)
                
                # Format environment data
                env_message = self.format_environment_display(match_data, full_match_data)
                
                # Create the detailed alert message
                message = (f"ALERT TYPE: 3 O/U Started\n"
                           f"----- MATCH SUMMARY -----\n"
                           f"Competition ID: {match_data.get('competition_id', 'Unknown')}\n"
                           f"Competition: {competition_name}\n"
                           f"Match: {home_team} vs {away_team}\n"
                           f"Score: {match_data.get('home_score', 0)} - {match_data.get('away_score', 0)}\n"
                           f"Status: First half (Minute: {match_minute}, Status ID: {status_id})\n\n"
                           f"{odds_message}\n\n"
                           f"{env_message}")
                
                return True, message
                
        except Exception as e:
            print(f"Error checking 3 O/U Started for match {match_id}: {e}")
            
        return False, ""
    
    def format_odds_display(self, odds_data):
        """Format the odds data for display in the alert message"""
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
    
    def format_environment_display(self, match_data, full_match_data):
        """Format the environment data for display in the alert message"""
        # Get environment data
        weather_code = full_match_data.get("weather_code", "")
        wind = full_match_data.get("wind", "")
        humidity = full_match_data.get("humidity", "")
        
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
