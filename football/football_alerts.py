#!/usr/bin/env python3
"""
Football Alerts System
Uses data from live.py to send alerts through Telegram when matches meet defined criteria
"""

import requests
import json
import time
import importlib
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import from live.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from football import live

# Telegram Bot Configuration
class TelegramBot:
    def __init__(self, token, chat_id):
        """
        Initialize the Telegram bot with token and chat_id
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}/"
        
    def send_message(self, message):
        """
        Send a message through the Telegram bot
        """
        url = f"{self.base_url}sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return None

# Alert Criteria Classes
class AlertCriteria:
    """Base class for alert criteria"""
    def __init__(self, name):
        self.name = name
        self.triggered_matches = set()  # Store match IDs that have already triggered alerts
    
    def check(self, match_data):
        """Check if the match meets the criteria (to be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_alert(self, match_data, home_team, away_team, competition_name):
        """Format the alert message (can be overridden by subclasses)"""
        return f"⚽ <b>ALERT: {self.name}</b>\n\n" \
               f"<b>{home_team} vs {away_team}</b>\n" \
               f"Competition: {competition_name}\n" \
               f"Score: {match_data.get('home_score', 0)} - {match_data.get('away_score', 0)}\n" \
               f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

class GoalScoredAlert(AlertCriteria):
    """Alert when a goal is scored in a match"""
    def __init__(self):
        super().__init__("Goal Scored")
        self.previous_scores = {}  # Store previous scores for comparison
    
    def check(self, match_data, home_team, away_team, competition_name):
        match_id = match_data.get('id')
        home_score = match_data.get('home_score', 0)
        away_score = match_data.get('away_score', 0)
        current_score = (home_score, away_score)
        
        # Get previous score, default to (0,0) if not seen before
        previous_score = self.previous_scores.get(match_id, (0, 0))
        
        # Update the stored score for next time
        self.previous_scores[match_id] = current_score
        
        # Check if the score changed (goal scored)
        if current_score != previous_score and match_id not in self.triggered_matches:
            # Only add to triggered matches if we've seen this match before
            # (prevents alerts for all matches when first running)
            if match_id in self.previous_scores:
                self.triggered_matches.add(match_id)
                return True, f"⚽ <b>GOAL SCORED!</b>\n\n" \
                        f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n" \
                        f"Competition: {competition_name}\n" \
                        f"Previous Score: {previous_score[0]} - {previous_score[1]}\n" \
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Remove from triggered matches if enough time has passed to allow new alerts
        elif current_score != previous_score and match_id in self.triggered_matches:
            self.triggered_matches.remove(match_id)
            
        return False, ""

class HalfTimeAlert(AlertCriteria):
    """Alert when a match reaches half-time"""
    def __init__(self):
        super().__init__("Half-Time")
        self.previous_status = {}
    
    def check(self, match_data, home_team, away_team, competition_name):
        match_id = match_data.get('id')
        status_id = match_data.get('status_id')
        
        # Get previous status
        previous_status = self.previous_status.get(match_id)
        
        # Update stored status
        self.previous_status[match_id] = status_id
        
        # Check if the match just reached half-time (status_id 3)
        if status_id == 3 and previous_status != 3 and match_id not in self.triggered_matches:
            self.triggered_matches.add(match_id)
            return True, f"⏱️ <b>HALF-TIME!</b>\n\n" \
                   f"<b>{home_team} {match_data.get('home_score', 0)} - {match_data.get('away_score', 0)} {away_team}</b>\n" \
                   f"Competition: {competition_name}\n" \
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # If the match moved past half-time, allow new alerts next time
        elif status_id != 3 and previous_status == 3 and match_id in self.triggered_matches:
            self.triggered_matches.remove(match_id)
            
        return False, ""

class MatchEndAlert(AlertCriteria):
    """Alert when a match ends"""
    def __init__(self):
        super().__init__("Match Ended")
        self.previous_status = {}
    
    def check(self, match_data, home_team, away_team, competition_name):
        match_id = match_data.get('id')
        status_id = match_data.get('status_id')
        
        # Get previous status
        previous_status = self.previous_status.get(match_id)
        
        # Update stored status
        self.previous_status[match_id] = status_id
        
        # Check if the match just ended (status_id 7 or 8)
        if status_id in [7, 8] and previous_status not in [7, 8] and match_id not in self.triggered_matches:
            self.triggered_matches.add(match_id)
            home_score = match_data.get('home_score', 0)
            away_score = match_data.get('away_score', 0)
            
            result_text = "DRAW"
            if home_score > away_score:
                result_text = f"{home_team} WINS"
            elif away_score > home_score:
                result_text = f"{away_team} WINS"
            
            return True, f"🏁 <b>MATCH ENDED: {result_text}!</b>\n\n" \
                   f"<b>{home_team} {home_score} - {away_score} {away_team}</b>\n" \
                   f"Competition: {competition_name}\n" \
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        return False, ""

class HighOddsAlert(AlertCriteria):
    """Alert when a match has unusually high odds"""
    def __init__(self, threshold=400):
        super().__init__(f"High Odds (>{threshold})")
        self.threshold = threshold
        self.check_interval = 300  # Check again every 5 minutes (300 seconds)
        self.last_trigger_time = {}
    
    def check(self, match_data, home_team, away_team, competition_name):
        match_id = match_data.get('id')
        current_time = time.time()
        
        # If we checked recently, skip
        if match_id in self.last_trigger_time and current_time - self.last_trigger_time[match_id] < self.check_interval:
            return False, ""
        
        # Fetch odds data
        odds_data = live.fetch_match_odds(match_id)
        formatted_odds = live.format_match_odds(odds_data)
        
        if not formatted_odds:
            return False, ""
        
        # Check ML odds
        high_odds_found = False
        odds_description = []
        
        if "ML" in formatted_odds and formatted_odds["ML"]:
            for entry in formatted_odds["ML"]:
                home_win = entry.get("home_win", 0)
                draw = entry.get("draw", 0)
                away_win = entry.get("away_win", 0)
                
                # Check if any value exceeds threshold (using American odds)
                if home_win >= self.threshold:
                    high_odds_found = True
                    odds_description.append(f"Home win: {live.decimal_to_american_str(home_win)}")
                if draw >= self.threshold:
                    high_odds_found = True
                    odds_description.append(f"Draw: {live.decimal_to_american_str(draw)}")
                if away_win >= self.threshold:
                    high_odds_found = True
                    odds_description.append(f"Away win: {live.decimal_to_american_str(away_win)}")
        
        if high_odds_found and match_id not in self.triggered_matches:
            self.triggered_matches.add(match_id)
            self.last_trigger_time[match_id] = current_time
            
            return True, f"💰 <b>HIGH ODDS DETECTED!</b>\n\n" \
                   f"<b>{home_team} vs {away_team}</b>\n" \
                   f"Competition: {competition_name}\n" \
                   f"High odds: {', '.join(odds_description)}\n" \
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Reset triggered state after a while
        elif match_id in self.triggered_matches and current_time - self.last_trigger_time.get(match_id, 0) > self.check_interval * 2:
            self.triggered_matches.remove(match_id)
            
        return False, ""

class AlertManager:
    """Manager for handling multiple alert criteria"""
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.criteria = []
    
    def add_criteria(self, criteria):
        """Add an alert criteria to the manager"""
        self.criteria.append(criteria)
    
    def check_all_matches(self):
        """Check all live matches against all criteria"""
        try:
            # Fetch live matches
            live_matches_data = live.fetch_live_matches()
            if not live_matches_data or "results" not in live_matches_data:
                print("No live matches found.")
                return
            
            # Extract match IDs
            match_ids = live.extract_match_ids(live_matches_data)
            print(f"\n===== CHECKING {len(match_ids)} LIVE FOOTBALL MATCHES FOR ALERTS =====\n")
            
            # Process each match ID
            for match_id in match_ids:
                try:
                    # Get match data from the live endpoint
                    live_match_data = None
                    for match in live_matches_data["results"]:
                        if match["id"] == match_id:
                            live_match_data = match
                            break
                    
                    if not live_match_data:
                        continue
                    
                    # Fetch additional match details from the recent/list endpoint
                    match_details_data = live.fetch_match_details(match_id)
                    
                    # Get match details from the response
                    match_details = None
                    if match_details_data and "results" in match_details_data and match_details_data["results"]:
                        if isinstance(match_details_data["results"], list):
                            match_details = match_details_data["results"][0]
                        else:
                            match_details = match_details_data["results"]
                    
                    # Combine data from both endpoints
                    match_data = live_match_data.copy()
                    
                    # Add or override with details data if available
                    if match_details:
                        match_data.update({k: v for k, v in match_details.items() if k not in match_data or not match_data[k]})
                    
                    # Get team and competition names
                    home_team_id = match_data.get("home_team_id", "")
                    away_team_id = match_data.get("away_team_id", "")
                    competition_id = match_data.get("competition_id", "")
                    
                    home_team_info = live.fetch_team_info(home_team_id) if home_team_id else None
                    away_team_info = live.fetch_team_info(away_team_id) if away_team_id else None
                    competition_info = live.fetch_competition_info(competition_id) if competition_id else None
                    
                    home_team_name = live.extract_team_name(home_team_info) if home_team_info else "Unknown Home Team"
                    away_team_name = live.extract_team_name(away_team_info) if away_team_info else "Unknown Away Team"
                    
                    competition_name = live.extract_competition_info(competition_info)[0] if competition_info else "Unknown Competition"
                    
                    # Check all criteria for this match
                    for criteria in self.criteria:
                        triggered, message = criteria.check(match_data, home_team_name, away_team_name, competition_name)
                        if triggered:
                            print(f"Alert triggered: {criteria.name} for {home_team_name} vs {away_team_name}")
                            self.bot.send_message(message)
                            
                except Exception as e:
                    print(f"Error processing match {match_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error checking matches: {e}")

def main():
    """Main function to run the alerts system"""
    # Set up Telegram bot (with your token and chat ID)
    telegram_token = "7764953908:AAHMpJsw5vKQYPiJGWrj0PgDkztiIgY_dko"
    telegram_chat_id = "6128359776"
    
    # Check if command line arguments are provided for token and chat ID
    if len(sys.argv) >= 3:
        telegram_token = sys.argv[1]
        telegram_chat_id = sys.argv[2]
    elif len(sys.argv) >= 2:
        # Allow just providing the chat ID with the default token
        telegram_chat_id = sys.argv[1]
    
    # If chat ID is still the default, prompt the user
    if telegram_chat_id == "6128359776":
        print("Please provide your Telegram chat ID:")
        telegram_chat_id = input("Chat ID: ").strip()
        
    bot = TelegramBot(telegram_token, telegram_chat_id)
    
    # Create alert manager and add criteria
    manager = AlertManager(bot)
    
    # Import our custom alerts
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "alerts"))
        from alerts.HighLineHalftimeZero import HighLineHalftimeZeroAlert
        from alerts.ThreeHtZero import ThreeHtZeroAlert
        from alerts.match_start.three_ou import ThreeOUStartAlert
        
        # Add the custom alerts
        manager.add_criteria(HighLineHalftimeZeroAlert())
        manager.add_criteria(ThreeHtZeroAlert())
        manager.add_criteria(ThreeOUStartAlert())
        print("Custom alerts loaded successfully.")
    except Exception as e:
        print(f"Error loading custom alerts: {e}")
    
    # Add our standard alert criteria
    manager.add_criteria(GoalScoredAlert())
    manager.add_criteria(HalfTimeAlert())
    manager.add_criteria(MatchEndAlert())
    manager.add_criteria(HighOddsAlert(threshold=400))
    
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Starting Football Alerts System at {start_time}")
    
    # Send startup notification
    start_message = f"🚀 <b>Football Alerts System Started</b>\n" \
                    f"Time: {start_time}\n" \
                    f"Monitoring live matches for alerts."
    bot.send_message(start_message)
    
    try:
        # Check matches in a loop
        while True:
            manager.check_all_matches()
            print(f"Completed check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Waiting 30 seconds...")
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nAlert system stopped by user at {stop_time}.")
        
        # Send shutdown notification
        stop_message = f"⚠️ <b>Football Alerts System Stopped</b>\n" \
                      f"Time: {stop_time}\n" \
                      f"System was manually stopped."
        bot.send_message(stop_message)
    except Exception as e:
        stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"Error in alert system: {e}"
        print(error_msg)
        
        # Send error notification
        error_message = f"❌ <b>Football Alerts System Error</b>\n" \
                       f"Time: {stop_time}\n" \
                       f"Error: {error_msg}"
        bot.send_message(error_message)

if __name__ == "__main__":
    main()
