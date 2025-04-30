#!/usr/bin/env python3
"""
Fetch raw JSON for a specific match from TheSports API
"""

import sys
import requests
import json
import os

# Import from football/live.py to use the same API credentials
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from football import live

def fetch_match_json(match_id=None, competition_id=None, team_name=None):
    """Fetch raw JSON for a match from TheSports API"""
    # Use the same API credentials as in live.py
    api_credentials = {
        'user': 'thenecpt',
        'secret': '0c55322e8e196d6ef9066fa4252cf386'
    }
    
    # Fetch live matches data
    live_url = 'https://api.thesports.com/v1/football/match/detail_live'
    response = requests.get(live_url, params=api_credentials)
    data = response.json()
    
    # Print the raw response
    print("Raw API Response:")
    print(json.dumps(data, indent=2))
    
    # Find the specific match if criteria provided
    if match_id or competition_id or team_name:
        matches = data.get('results', [])
        if len(matches) > 0:
            filtered_matches = []
            
            for match in matches:
                if match_id and match.get('id') == match_id:
                    filtered_matches.append(match)
                elif competition_id and match.get('competition_id') == competition_id:
                    if not team_name or team_name.lower() in match.get('home_team_name', '').lower() or team_name.lower() in match.get('away_team_name', '').lower():
                        filtered_matches.append(match)
                elif team_name and (team_name.lower() in match.get('home_team_name', '').lower() or team_name.lower() in match.get('away_team_name', '').lower()):
                    filtered_matches.append(match)
            
            if filtered_matches:
                print("\nFiltered Matches:")
                print(json.dumps(filtered_matches, indent=2))
            else:
                print("\nNo matches found matching the criteria.")
        else:
            print("\nNo live matches found.")
    
    # Also fetch odds data
    odds_url = 'https://api.thesports.com/v1/football/odds/history'
    params = api_credentials.copy()
    response = requests.get(odds_url, params=params)
    odds_data = response.json()
    
    print("\nRaw Odds API Response:")
    print(json.dumps(odds_data, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        team_name = sys.argv[1]
        competition_id = sys.argv[2] if len(sys.argv) > 2 else None
        fetch_match_json(competition_id=competition_id, team_name=team_name)
    else:
        fetch_match_json()
