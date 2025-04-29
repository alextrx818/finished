#!/usr/bin/env python3
"""
Base alert criteria classes for the Football Alerts System
"""

from datetime import datetime

class AlertCriteria:
    """Base class for all alert criteria"""
    
    def __init__(self, name, description=""):
        """
        Initialize the alert criteria
        
        Args:
            name (str): Name of the alert
            description (str): Optional description of what the alert does
        """
        self.name = name
        self.description = description
        self.triggered_matches = set()  # Store match IDs that have already triggered alerts
    
    def check(self, match_data, home_team, away_team, competition_name):
        """
        Check if the match meets the criteria
        
        Args:
            match_data (dict): Match data from the API
            home_team (str): Name of the home team
            away_team (str): Name of the away team
            competition_name (str): Name of the competition
            
        Returns:
            tuple: (bool, str) - Whether the alert was triggered and the alert message
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_alert(self, match_data, home_team, away_team, competition_name):
        """
        Format the alert message
        
        Args:
            match_data (dict): Match data from the API
            home_team (str): Name of the home team
            away_team (str): Name of the away team
            competition_name (str): Name of the competition
            
        Returns:
            str: Formatted alert message
        """
        home_score = match_data.get('home_score', 0)
        away_score = match_data.get('away_score', 0)
        status_id = match_data.get('status_id', 0)
        status_name = self.get_status_name(status_id)
        
        return (f"⚽ <b>ALERT: {self.name}</b>\n\n"
                f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n"
                f"Competition: {competition_name}\n"
                f"Status: {status_name} (ID: {status_id})\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_status_name(self, status_id):
        """
        Get the name of a match status by ID
        
        Args:
            status_id (int): Match status ID
            
        Returns:
            str: Status name
        """
        status_map = {
            0: "Not started",
            1: "First half",
            2: "Half-time",
            3: "Second half",
            4: "Extra time",
            5: "Penalties",
            6: "Finished",
            7: "Finished after extra time",
            8: "Finished after penalties",
            9: "Postponed",
            10: "Cancelled",
            11: "Abandoned",
            12: "Interrupted",
            13: "Suspended",
            14: "Awarded",
            15: "Delayed",
            16: "To be announced",
            17: "First half, extra",
            18: "Second half, extra",
            19: "After penalties"
        }
        return status_map.get(status_id, f"Unknown status ({status_id})")
