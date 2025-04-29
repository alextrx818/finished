#!/usr/bin/env python3
"""
High Line Halftime Zero Alert
Alert when a match with high expected goals (Over/Under 3.0+) reaches halftime with 0-0 score
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import from the main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from football_alerts import AlertCriteria
from football import live

class HighLineHalftimeZeroAlert(AlertCriteria):
    """
    High Line Halftime Zero Alert
    
    Alert when:
    1. A match has an Over/Under line of 3.0 or higher at minutes 4-6
    2. The match reaches halftime (status_id = 3)
    3. The score is 0-0
    """
    
    def __init__(self):
        super().__init__("High Line Halftime Zero")
        self.high_line_matches = {}  # Match ID -> Over/Under line value
        self.previous_status = {}    # Track previous match status
        
    def check(self, match_data, home_team, away_team, competition_name):
        """
        Check if the match meets the criteria:
        - Has Over/Under line >= 3.0 at minutes 4-6
        - Is at halftime
        - Score is 0-0
        
        Returns:
            tuple: (bool, str) - Whether the alert was triggered and the alert message
        """
        match_id = match_data.get('id')
        if not match_id:
            return False, ""
            
        # Check current match status and score
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
                                    # Store the line value for this match
                                    self.high_line_matches[match_id] = line_value
                                    print(f"Match {match_id} ({home_team} vs {away_team}) tracked with high line {line_value}")
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
            
            # Get the line value we stored
            line_value = self.high_line_matches[match_id]
            
            # Create the alert message
            message = (f"🎯 <b>HIGH LINE HALFTIME ZERO ALERT</b>\n\n"
                       f"<b>{home_team} 0-0 {away_team}</b>\n"
                       f"Competition: {competition_name}\n"
                       f"Status: Half-Time\n"
                       f"Over/Under Line: {line_value}\n"
                       f"Betting Insight: Match expected {line_value}+ goals, but 0-0 at HT\n"
                       f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True, message
            
        # Remove from triggered matches once the match leaves halftime
        # This allows for new alerts if the match somehow returns to halftime
        elif not is_halftime and match_id in self.triggered_matches:
            self.triggered_matches.remove(match_id)
            
        return False, ""
