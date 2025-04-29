import requests
import json
import sys

# API credentials
USER = "thenecpt"
SECRET = "0c55322e8e196d6ef9066fa4252cf386"

def fetch_match_odds(match_id):
    """
    Fetch odds history for a specific match ID and print the raw JSON
    """
    url = "https://api.thesports.com/v1/football/odds/history"
    params = {
        "user": USER,
        "secret": SECRET,
        "uuid": match_id
    }
    
    print(f"Fetching odds for match ID: {match_id}")
    print(f"URL: {url}?user={USER}&secret={SECRET}&uuid={match_id}")
    
    try:
        session = requests.Session()
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds for match {match_id}: {e}")
        return None

def decimal_to_american(decimal_odds):
    """
    Convert decimal odds to American format
    - For odds < 2.0: -100/(odds-1)
    - For odds >= 2.0: (odds-1)*100
    """
    try:
        decimal = float(decimal_odds)
        if decimal < 2.0:
            american = int(-100 / (decimal - 1))
        else:
            american = int((decimal - 1) * 100)
        return american
    except (ValueError, ZeroDivisionError):
        return 0

def format_match_odds(odds_data):
    """
    Format the odds data according to the required structure:
    - SPREAD (Asia handicap)
    - ML (European odds)
    - Over/Under (bs - Big Small)
    """
    if not odds_data or "code" not in odds_data or odds_data["code"] != 0:
        return {}
    
    if "results" not in odds_data:
        return {}
    
    formatted_odds = {
        "SPREAD": [],
        "ML": [],
        "Over/Under": []
    }
    
    # Handle the case where results is a dictionary rather than a list
    results = odds_data["results"]
    
    # The structure is {"results": {"bookmaker_id": {"odds_type": [odds_entries]}}}
    for bookmaker_id, bookmaker_data in results.items():
        # Process Asia handicap (SPREAD)
        if "asia" in bookmaker_data:
            for asia_entry in bookmaker_data["asia"]:
                if len(asia_entry) >= 4:
                    time_of_match = asia_entry[1] if asia_entry[1] else "pre-match"
                    home_win_decimal = asia_entry[2]
                    handicap = asia_entry[3]
                    away_win_decimal = asia_entry[4]
                    
                    spread_entry = {
                        "time_of_match": time_of_match,
                        "home_win": decimal_to_american(home_win_decimal),
                        "handicap": handicap,
                        "away_win": decimal_to_american(away_win_decimal)
                    }
                    formatted_odds["SPREAD"].append(spread_entry)
        
        # Process European odds (ML)
        if "euro" in bookmaker_data:
            for euro_entry in bookmaker_data["euro"]:
                if len(euro_entry) >= 4:
                    time_of_match = euro_entry[1] if euro_entry[1] else "pre-match"
                    home_win_decimal = euro_entry[2]
                    draw_decimal = euro_entry[3]
                    away_win_decimal = euro_entry[4]
                    
                    ml_entry = {
                        "time_of_match": time_of_match,
                        "home_win": decimal_to_american(home_win_decimal),
                        "draw": decimal_to_american(draw_decimal),
                        "away_win": decimal_to_american(away_win_decimal)
                    }
                    formatted_odds["ML"].append(ml_entry)
        
        # Process Big Small (Over/Under)
        if "bs" in bookmaker_data:
            for bs_entry in bookmaker_data["bs"]:
                if len(bs_entry) >= 4:
                    time_of_match = bs_entry[1] if bs_entry[1] else "pre-match"
                    over_decimal = bs_entry[2]
                    handicap = bs_entry[3]
                    under_decimal = bs_entry[4]
                    
                    ou_entry = {
                        "time_of_match": time_of_match,
                        "over": decimal_to_american(over_decimal),
                        "handicap": handicap,
                        "under": decimal_to_american(under_decimal)
                    }
                    formatted_odds["Over/Under"].append(ou_entry)
    
    return formatted_odds

def main():
    if len(sys.argv) < 2:
        print("Usage: python odds_dump.py <match_id>")
        return
    
    match_id = sys.argv[1]
    odds_data = fetch_match_odds(match_id)
    
    if odds_data:
        print("\n--- RAW ODDS DATA ---")
        print(json.dumps(odds_data, indent=2))
        
        # Format and display the odds in the required format
        formatted_odds = format_match_odds(odds_data)
        
        print("\n--- FORMATTED ODDS ---")
        print(json.dumps(formatted_odds, indent=2))
        
        # Display a simple summary of the most recent odds
        print("\n--- ODDS SUMMARY ---")
        
        # SPREAD odds
        if formatted_odds["SPREAD"]:
            spread = formatted_odds["SPREAD"][-1]
            print(f"SPREAD: Time: {spread['time_of_match']} | Home: {spread['home_win']:+d} | Handicap: {spread['handicap']} | Away: {spread['away_win']:+d}")
        
        # ML odds
        if formatted_odds["ML"]:
            ml = formatted_odds["ML"][-1]
            print(f"ML: Time: {ml['time_of_match']} | Home: {ml['home_win']:+d} | Draw: {ml['draw']:+d} | Away: {ml['away_win']:+d}")
        
        # Over/Under odds
        if formatted_odds["Over/Under"]:
            ou = formatted_odds["Over/Under"][-1]
            print(f"OVER/UNDER: Time: {ou['time_of_match']} | Over: {ou['over']:+d} | Line: {ou['handicap']} | Under: {ou['under']:+d}")
        
    else:
        print("No odds data received")

if __name__ == "__main__":
    main()
