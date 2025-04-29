import requests
import json
import time
from functools import lru_cache
import sys
import traceback

# Create a single session for all API calls
session = requests.Session()

# API credentials
USER = "thenecpt"
SECRET = "0c55322e8e196d6ef9066fa4252cf386"

def fetch_live_matches():
    """
    Fetch all live football matches from the API
    """
    url = "https://api.thesports.com/v1/football/match/detail_live"
    params = {
        "user": USER,
        "secret": SECRET
    }
    
    try:
        print("Fetching live matches...")
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live matches: {e}")
        return None

def fetch_match_details(match_id):
    """
    Fetch detailed information for a specific match ID
    """
    url = "https://api.thesports.com/v1/football/match/recent/list"
    params = {
        "user": USER,
        "secret": SECRET,
        "uuid": match_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for match {match_id}: {e}")
        return None

@lru_cache(maxsize=None)
def fetch_team_info(team_id):
    """
    Fetch team information using the team ID (cached)
    """
    url = "https://api.thesports.com/v1/football/team/additional/list"
    params = {
        "user": USER,
        "secret": SECRET,
        "uuid": team_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching team info for {team_id}: {e}")
        return None

@lru_cache(maxsize=None)
def fetch_competition_info(competition_id):
    """
    Fetch competition information using the competition ID (cached)
    """
    url = "https://api.thesports.com/v1/football/competition/additional/list"
    params = {
        "user": USER,
        "secret": SECRET,
        "uuid": competition_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching competition info for {competition_id}: {e}")
        return None

def fetch_country_data():
    """
    Fetch all country data
    """
    url = "https://api.thesports.com/v1/football/country/list"
    params = {
        "user": USER,
        "secret": SECRET
    }
    
    try:
        print("Fetching country data...")
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching country data: {e}")
        return None

def extract_match_ids(matches_data):
    """
    Extract all match IDs from the live matches data
    """
    match_ids = []
    
    if not matches_data or "results" not in matches_data:
        return match_ids
    
    for match in matches_data["results"]:
        if "id" in match:
            match_ids.append(match["id"])
    
    return match_ids

def extract_team_name(team_data):
    """
    Extract team name from team data
    """
    if not team_data or "code" not in team_data or team_data["code"] != 0:
        return "Unknown Team"
    
    if "results" not in team_data or not team_data["results"]:
        return "Unknown Team"
    
    team_results = team_data["results"]
    team = team_results[0] if isinstance(team_results, list) and team_results else team_results
    
    return team.get("name", "Unknown Team")

def extract_competition_info(competition_data):
    """
    Extract competition name and country ID from competition data
    """
    competition_name = "Unknown Competition"
    country_id = ""
    
    if not competition_data or "code" not in competition_data or competition_data["code"] != 0:
        return competition_name, country_id
    
    if "results" not in competition_data or not competition_data["results"]:
        return competition_name, country_id
    
    comp_results = competition_data["results"]
    comp = comp_results[0] if isinstance(comp_results, list) and comp_results else comp_results
    
    competition_name = comp.get("name", "Unknown Competition")
    
    # Extract country ID if available
    # Check different possible locations for country ID
    if "country_id" in comp:
        country_id = comp.get("country_id", "")
    elif "country" in comp and comp["country"]:
        if isinstance(comp["country"], dict):
            country_id = comp["country"].get("id", "")
        else:
            country_id = comp["country"]
    
    return competition_name, country_id

def create_country_id_to_name_map(country_data):
    """
    Create a dictionary mapping country IDs to country names
    """
    country_map = {}
    
    if not country_data or "code" not in country_data or country_data["code"] != 0:
        return country_map
    
    if "results" not in country_data or not country_data["results"]:
        return country_map
    
    for country in country_data["results"]:
        if "id" in country and "name" in country:
            country_map[country["id"]] = country["name"]
    
    return country_map

def get_weather_description(weather_code):
    """
    Convert numeric weather code to a human-readable description
    """
    weather_codes = {
        "1": "Partially cloudy",
        "2": "Cloudy",
        "3": "Foggy",
        "4": "Rainy",
        "5": "Sunny",
        "6": "Snowy",
        "7": "Windy"
    }
    
    # Handle both string and integer codes
    if isinstance(weather_code, str) and weather_code.isdigit():
        code = weather_code
    elif isinstance(weather_code, int):
        code = str(weather_code)
    else:
        code = str(weather_code)
    
    return weather_codes.get(code, f"Unknown ({code})")

def celsius_to_fahrenheit(celsius_str):
    """
    Convert celsius temperature string to fahrenheit
    """
    try:
        # Extract numeric part from temperature string (e.g., "20°C" -> "20")
        celsius_value = float(celsius_str.replace('°C', '').strip())
        # Convert to Fahrenheit: F = (C * 9/5) + 32
        fahrenheit_value = (celsius_value * 9/5) + 32
        return f"{fahrenheit_value:.1f}°F"
    except (ValueError, AttributeError):
        return celsius_str  # Return original if conversion fails

def meters_per_second_to_mph(mps_str):
    """
    Convert wind speed from m/s to mph
    """
    try:
        # Extract numeric part from wind string (e.g., "2.0m/s" -> "2.0")
        mps_value = float(mps_str.replace('m/s', '').strip())
        # Convert to mph: 1 m/s = 2.237 mph
        mph_value = mps_value * 2.237
        return f"{mph_value:.1f} mph"
    except (ValueError, AttributeError):
        return mps_str  # Return original if conversion fails

def fetch_match_odds(match_id):
    """
    Fetch odds history for a specific match ID
    """
    url = "https://api.thesports.com/v1/football/odds/history"
    params = {
        "user": USER,
        "secret": SECRET,
        "uuid": match_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds for match {match_id}: {e}")
        return None

def decimal_to_american(decimal_odds):
    """
    Convert decimal odds to American odds (int value)
    For odds > 2.0: (decimal - 1) * 100
    For odds < 2.0: -100 / (decimal - 1)
    """
    try:
        decimal_odds = float(decimal_odds)
        if decimal_odds == 0:
            return 0
        
        if decimal_odds >= 2.0:
            return int(round((decimal_odds - 1) * 100))
        else:
            return int(round(-100 / (decimal_odds - 1)))
    except (ValueError, ZeroDivisionError):
        return 0

def decimal_to_american_str(decimal_odds):
    """
    Convert decimal odds to American odds with + or - prefix
    """
    try:
        decimal_odds = float(decimal_odds)
        if decimal_odds == 0:
            return "0"
            
        if decimal_odds >= 2.0:
            return f"+{int(round((decimal_odds - 1) * 100))}"
        else:
            return f"{int(round(-100 / (decimal_odds - 1)))}"
    except (ValueError, ZeroDivisionError):
        return "0"

def hk_to_american(hk_odds):
    """
    Convert Hong Kong odds to American odds (int value)
    """
    try:
        hk_odds = float(hk_odds)
        if hk_odds >= 1:
            return int(round(hk_odds * 100))
        else:
            return int(round(-100 / hk_odds))
    except (ValueError, ZeroDivisionError):
        return 0

def hk_to_american_str(hk_odds):
    """
    Convert Hong Kong odds to American odds with + or - prefix
    """
    try:
        hk_odds = float(hk_odds)
        if hk_odds >= 1:
            return f"+{int(round(hk_odds * 100))}"
        else:
            return f"{int(round(-100 / hk_odds))}"
    except (ValueError, ZeroDivisionError):
        return "0"

def format_match_odds(odds_data):
    """
    Format the odds data according to the required structure:
    - SPREAD (Asia handicap)
    - ML (European odds)
    - Over/Under (Big Small)
    
    Filter all odds types to only include minutes 4-6
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
    
    # Print raw data for SPREAD and ML for debugging
    print("\nDEBUG: Raw odds data used for calculation:")
    for bookmaker_id, bookmaker_data in results.items():
        if "asia" in bookmaker_data and bookmaker_data["asia"]:
            print(f"SPREAD (Asia) - Bookmaker {bookmaker_id} sample: {bookmaker_data['asia'][0]}")
        if "eu" in bookmaker_data and bookmaker_data["eu"]:
            print(f"ML (EU) - Bookmaker {bookmaker_id} sample: {bookmaker_data['eu'][0]}")
        if "bs" in bookmaker_data and bookmaker_data["bs"]:
            print(f"Over/Under (BS) - Bookmaker {bookmaker_id} sample: {bookmaker_data['bs'][0]}")
    
    # The structure is {"results": {"bookmaker_id": {"odds_type": [odds_entries]}}}
    for bookmaker_id, bookmaker_data in results.items():
        # Process Asia handicap (SPREAD)
        if "asia" in bookmaker_data:
            target_minutes_entries = []
            other_entries = []
            
            for asia_entry in bookmaker_data["asia"]:
                if len(asia_entry) >= 5:
                    time_of_match = asia_entry[1] if asia_entry[1] else "pre-match"
                    home_win_hk = asia_entry[2]
                    handicap = asia_entry[3]
                    away_win_hk = asia_entry[4]
                    
                    spread_entry = {
                        "time_of_match": time_of_match,
                        "home_win": hk_to_american(home_win_hk),
                        "handicap": handicap,
                        "away_win": hk_to_american(away_win_hk)
                    }
                    
                    # Check if time_of_match is numeric
                    try:
                        minute = int(time_of_match) if time_of_match.isdigit() else 0
                        # Only include minutes 4-6 as requested
                        if minute >= 4 and minute <= 6:
                            target_minutes_entries.append(spread_entry)
                        else:
                            other_entries.append(spread_entry)
                    except (ValueError, TypeError):
                        # Not a numeric minute, add to other entries
                        other_entries.append(spread_entry)
            
            # Add target minutes entries if they exist (prioritized)
            if target_minutes_entries:
                formatted_odds["SPREAD"].extend(target_minutes_entries)
            # Otherwise add the other entries
            elif other_entries:
                formatted_odds["SPREAD"].extend(other_entries)
        
        # Process European odds (ML) - ONLY FOR BOOKMAKER 2
        if bookmaker_id == "2" and "eu" in bookmaker_data:
            target_minutes_entries = []
            other_entries = []
            
            for euro_entry in bookmaker_data["eu"]:
                if len(euro_entry) >= 5:
                    time_of_match = euro_entry[1] if euro_entry[1] else "pre-match"
                    home_win_decimal = float(euro_entry[2])  # Home win odds (decimal)
                    draw_decimal = float(euro_entry[3])      # Draw odds (decimal)
                    away_win_decimal = float(euro_entry[4])  # Away win odds (decimal)
                    
                    # Directly apply the conversion formula
                    if home_win_decimal >= 2.0:
                        home_win = int(round((home_win_decimal - 1) * 100))
                    else:
                        home_win = int(round(-100 / (home_win_decimal - 1)))
                        
                    if draw_decimal >= 2.0:
                        draw = int(round((draw_decimal - 1) * 100))
                    else:
                        draw = int(round(-100 / (draw_decimal - 1)))
                        
                    if away_win_decimal >= 2.0:
                        away_win = int(round((away_win_decimal - 1) * 100))
                    else:
                        away_win = int(round(-100 / (away_win_decimal - 1)))
                    
                    # Add detailed debugging for this conversion
                    print(f"DEBUG EU CONVERSION: Entry time {time_of_match}")
                    print(f"  Home: {home_win_decimal} → {home_win}")
                    print(f"  Draw: {draw_decimal} → {draw}")
                    print(f"  Away: {away_win_decimal} → {away_win}")
                    
                    ml_entry = {
                        "time_of_match": time_of_match,
                        "home_win": home_win,
                        "draw": draw,
                        "away_win": away_win
                    }
                    
                    # Specifically look for minutes 4, 5, or 6 for all odds as requested
                    if time_of_match in ["4", "5", "6"]:
                        target_minutes_entries.append(ml_entry)
                    else:
                        other_entries.append(ml_entry)
            
            # Add target minutes entries if they exist (prioritized)
            if target_minutes_entries:
                formatted_odds["ML"].extend(target_minutes_entries)
            # Otherwise add the other entries
            else:
                formatted_odds["ML"].extend(other_entries)
        
        # Process Big Small (Over/Under)
        if "bs" in bookmaker_data:
            target_minutes_entries = []
            other_entries = []
            
            for bs_entry in bookmaker_data["bs"]:
                if len(bs_entry) >= 5:
                    time_of_match = bs_entry[1] if bs_entry[1] else "pre-match"
                    over_hk = bs_entry[2]
                    points_total = bs_entry[3]
                    under_hk = bs_entry[4]
                    
                    ou_entry = {
                        "time_of_match": time_of_match,
                        "over": hk_to_american(over_hk),
                        "handicap": points_total,
                        "under": hk_to_american(under_hk)
                    }
                    
                    # Check if time_of_match is numeric
                    try:
                        minute = int(time_of_match) if time_of_match.isdigit() else 0
                        # Only include minutes 4-6 as requested
                        if minute >= 4 and minute <= 6:
                            target_minutes_entries.append(ou_entry)
                        else:
                            other_entries.append(ou_entry)
                    except (ValueError, TypeError):
                        # Not a numeric minute, add to other entries
                        other_entries.append(ou_entry)
            
            # Add target minutes entries if they exist (prioritized)
            if target_minutes_entries:
                formatted_odds["Over/Under"].extend(target_minutes_entries)
            # Otherwise add the other entries
            elif other_entries:
                formatted_odds["Over/Under"].extend(other_entries)
    
    return formatted_odds

def get_latest_odds(odds_data, odds_type):
    """
    Get the latest odds entry for a specific odds type, prioritizing early game odds,
    with special handling for ML odds (minutes 4-6)
    """
    if not odds_data or odds_type not in odds_data or not odds_data[odds_type]:
        return None
    
    # For ML (Money Line), specifically prioritize minutes 4, 5, and 6
    if odds_type == "ML":
        # Find entries from minutes 4, 5, or 6 (specifically for ML odds)
        early_minutes = [entry for entry in odds_data[odds_type] 
                        if entry["time_of_match"] in ["4", "5", "6"]]
        
        # If we have early minute entries, return the latest one
        if early_minutes:
            return early_minutes[-1]
        
        # Otherwise return the latest entry
        return odds_data[odds_type][-1]
        
    # For SPREAD and Over/Under, filter entries to only include minutes 0-3 or minutes ≥ 7 (skip minutes 4-6)
    valid_entries = []
    for entry in odds_data[odds_type]:
        time_of_match = entry.get("time_of_match", "")
        try:
            # Try to convert to integer if it's a digit string
            if isinstance(time_of_match, str) and time_of_match.isdigit():
                minute = int(time_of_match)
                # Keep minutes 0-3 or minutes ≥ 7 (skip minutes 4-6)
                if minute <= 3 or minute >= 7:
                    valid_entries.append(entry)
            else:
                # Non-numeric time, add it
                valid_entries.append(entry)
        except (ValueError, TypeError):
            # Not convertible to integer, add it
            valid_entries.append(entry)
    
    # If no valid entries after filtering, return None
    if not valid_entries:
        return None
    
    # Separate early minutes (0-3) from other valid minutes
    early_minutes = [entry for entry in valid_entries 
                    if isinstance(entry.get("time_of_match", ""), str) 
                    and entry["time_of_match"].isdigit() 
                    and int(entry["time_of_match"]) <= 3]
    
    # If we have early minute entries, return the latest one
    if early_minutes:
        return early_minutes[-1]
    
    # Otherwise return the latest valid entry
    return valid_entries[-1]

# Now implementing parallelization with ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed

def format_american_odds(odds_value):
    """Format American odds with consistent sign display."""
    return f"{odds_value:+d}"

def format_odds_display(formatted_odds):
    """
    Format the odds for display
    """
    output = []
    
    # Display ML (European odds) FIRST
    if formatted_odds.get("ML"):
        # Sort by time and take the most relevant minute (4-6)
        ml_sorted = sorted(formatted_odds["ML"], key=lambda x: str(x.get("time_of_match", "")))
        
        # Try to find an entry from minutes 4-6
        ml_entry = None
        for entry in ml_sorted:
            time_str = entry.get("time_of_match", "")
            if time_str in ["4", "5", "6"]:
                ml_entry = entry
                break
        
        # If no entry from minutes 4-6, take the first available
        if not ml_entry and ml_sorted:
            ml_entry = ml_sorted[0]
        
        if ml_entry:
            ml_time = ml_entry.get("time_of_match", "")
            
            # Get the raw values for debugging
            home_win_raw = ml_entry.get("home_win", 0)
            draw_raw = ml_entry.get("draw", 0)
            away_win_raw = ml_entry.get("away_win", 0)
            
            # Format for display
            home_win = format_american_odds(home_win_raw)
            draw = format_american_odds(draw_raw)
            away_win = format_american_odds(away_win_raw)
            
            # Add debug info with better formatting
            print(f"DEBUG ML: Home: {home_win_raw} | Draw: {draw_raw} | Away: {away_win_raw}")
            
            # Add a note if this is not from the target minutes 4-6
            minutes_note = ""
            if ml_time not in ["4", "5", "6"]:
                minutes_note = " (No data from minutes 4-6 available)"
            
            output.append("ML (Money Line):")
            output.append(f"Time: {ml_time} min{minutes_note} | Home: {home_win} | Draw: {draw} | Away: {away_win}")
    
    # Display SPREAD (Asia handicap)
    if formatted_odds.get("SPREAD"):
        # Sort by time and take the earliest from minutes 4-6 if available
        spread_sorted = sorted(formatted_odds["SPREAD"], key=lambda x: str(x.get("time_of_match", "")))
        
        # Try to find an entry from minutes 4-6
        spread_entry = None
        for entry in spread_sorted:
            time_str = entry.get("time_of_match", "")
            if time_str in ["4", "5", "6"]:
                spread_entry = entry
                break
        
        # If no entry from minutes 4-6, take the first available
        if not spread_entry and spread_sorted:
            spread_entry = spread_sorted[0]
            
        if spread_entry:
            spread_time = spread_entry.get("time_of_match", "")
            home_odds = format_american_odds(spread_entry.get("home_win", 0))
            handicap = spread_entry.get("handicap", 0)
            away_odds = format_american_odds(spread_entry.get("away_win", 0))
            
            # Add a note if this is not from the target minutes 4-6
            minutes_note = ""
            if spread_time not in ["4", "5", "6"]:
                minutes_note = " (No data from minutes 4-6 available)"
            
            output.append("\nSPREAD (Asia Handicap):")
            output.append(f"Time: {spread_time} min{minutes_note} | Home: {home_odds} | Handicap: {handicap} | Away: {away_odds}")
    
    # Display Over/Under
    if formatted_odds.get("Over/Under"):
        # Sort by time and try to find entries from minutes 4-6
        ou_sorted = sorted(formatted_odds["Over/Under"], key=lambda x: str(x.get("time_of_match", "")))
        
        # Try to find an entry from minutes 4-6
        ou_entry = None
        for entry in ou_sorted:
            time_str = entry.get("time_of_match", "")
            if time_str in ["4", "5", "6"]:
                ou_entry = entry
                break
        
        # If no entry from minutes 4-6, take the first available
        if not ou_entry and ou_sorted:
            ou_entry = ou_sorted[0]
        
        if ou_entry:
            ou_time = ou_entry.get("time_of_match", "")
            over_odds = format_american_odds(ou_entry.get("over", 0))
            handicap = ou_entry.get("handicap", 0)
            under_odds = format_american_odds(ou_entry.get("under", 0))
            
            # Add a note if this is not from the target minutes 4-6
            minutes_note = ""
            if ou_time not in ["4", "5", "6"]:
                minutes_note = " (No data from minutes 4-6 available)"
            
            output.append("\nOver/Under:")
            output.append(f"Time: {ou_time} min{minutes_note} | Over: {over_odds} | Line: {handicap} | Under: {under_odds}")
    
    return "\n".join(output)

def main():
    """
    Main function to fetch live matches and print match details with team names and competition country using parallelization
    """
    try:
        # Load countries first so we have them available for competition lookup
        print("Fetching country data...")
        countries = fetch_country_data()
        country_map = create_country_id_to_name_map(countries)
        
        # Fetch live matches
        print("Fetching live matches...")
        live_matches_data = fetch_live_matches()
        if not live_matches_data or "results" not in live_matches_data:
            print("No live matches found.")
            return
        
        matches = live_matches_data["results"]
        print(f"\nFound {len(matches)} live matches.")
        
        # Optionally limit the number of matches for quicker results
        limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5  # Default to 5
        if limit < len(matches):
            print(f"Limiting to first {limit} matches for quicker results.")
            matches = matches[:limit]
        
        # Prepare for parallel processing
        match_ids = [match.get("id") for match in matches]
        
        print("Fetching match details in parallel...\n")
        
        # Process matches in parallel
        with ThreadPoolExecutor(max_workers=min(10, len(match_ids))) as executor:
            # Submit match detail fetching tasks
            detail_futures = {executor.submit(fetch_match_details, match_id): match_id for match_id in match_ids}
            
            # Process results as they complete
            for i, future in enumerate(as_completed(detail_futures), 1):
                match_id = detail_futures[future]
                try:
                    match_details = future.result()
                    if not match_details or "results" not in match_details:
                        print(f"No details found for match ID: {match_id}")
                        continue
                    
                    # Header for each match
                    print("=" * 30)
                    print(f"MATCH {i} of {len(match_ids)}")
                    print("=" * 30)
                    print(f"Processing match ID: {match_id}")
                    
                    match_data = match_details["results"][0] if match_details["results"] else None
                    if not match_data:
                        print(f"No data in results for match ID: {match_id}")
                        continue
                    
                    # Fetch team and competition info
                    print("Fetching team and competition data...")
                    home_team_id = match_data.get("home_team_id", "")
                    away_team_id = match_data.get("away_team_id", "")
                    competition_id = match_data.get("competition_id", "")
                    
                    home_team_info = fetch_team_info(home_team_id) if home_team_id else None
                    away_team_info = fetch_team_info(away_team_id) if away_team_id else None
                    competition_info = fetch_competition_info(competition_id) if competition_id else None
                    
                    home_team_name = extract_team_name(home_team_info) if home_team_info else "Unknown Home Team"
                    away_team_name = extract_team_name(away_team_info) if away_team_info else "Unknown Away Team"
                    
                    competition_name = extract_competition_info(competition_info)[0] if competition_info else "Unknown Competition"
                    competition_country_id = extract_competition_info(competition_info)[1] if competition_info else None
                    competition_country = country_map.get(competition_country_id, "Unknown Country")
                    
                    # Fetch odds data
                    print(f"Fetching odds data for match ID: {match_id}...")
                    odds_data = fetch_match_odds(match_id)
                    
                    # Print some debug info about the odds data
                    print("\nRaw odds data sample:")
                    if odds_data and "results" in odds_data:
                        results = odds_data["results"]
                        print(f"Results type: {type(results)}")
                        
                        # Debug for EU odds
                        for bookmaker_id, bookmaker_data in results.items():
                            if "eu" in bookmaker_data:
                                print("\nDetailed EU (Money Line) odds for bookmaker", bookmaker_id)
                                early_eu_entries = []
                                
                                # Filter to get entries from minutes 4-6
                                for entry in bookmaker_data["eu"]:
                                    if len(entry) >= 5 and entry[1] in ["4", "5", "6"]:
                                        early_eu_entries.append(entry)
                                
                                if early_eu_entries:
                                    print(f"Found {len(early_eu_entries)} EU entries from minutes 4-6:")
                                    for entry in early_eu_entries[:3]:  # Show first 3 entries
                                        print(f"Raw entry: {entry}")
                                        print(f"Parsed as: Time: {entry[1]}, Home: {entry[2]}, Draw: {entry[3]}, Away: {entry[4]}")
                                        print(f"Converted to American (Decimal odds): Time: {entry[1]}, "
                                              f"Home: {decimal_to_american_str(entry[2])}, Draw: {decimal_to_american_str(entry[3])}, "
                                              f"Away: {decimal_to_american_str(entry[4])}")
                                        print("-" * 40)
                                else:
                                    print("No early game EU entries found (minutes 4-6)")
                                    
                                    # Show any other entries
                                    other_entries = []
                                    for entry in bookmaker_data["eu"]:
                                        if len(entry) >= 5:
                                            other_entries.append(entry)
                                    
                                    if other_entries:
                                        print(f"Found {len(other_entries)} other EU entries:")
                                        for entry in other_entries[:1]:  # Show just the first one
                                            print(f"Raw entry: {entry}")
                                            print(f"Parsed as: Time: {entry[1]}, Home: {entry[2]}, Draw: {entry[3]}, Away: {entry[4]}")
                                            print(f"Converted to American (Decimal odds): Time: {entry[1]}, "
                                                  f"Home: {decimal_to_american_str(entry[2])}, Draw: {decimal_to_american_str(entry[3])}, "
                                                  f"Away: {decimal_to_american_str(entry[4])}")
                                            print("-" * 40)
                                break
                        
                        # Debug for BS odds
                        for bookmaker_id, bookmaker_data in results.items():
                            if "bs" in bookmaker_data:
                                print("\nDetailed BS (Over/Under) data for bookmaker", bookmaker_id)
                                early_bs_entries = []
                                
                                # Filter to get entries from minutes 1-3
                                for entry in bookmaker_data["bs"]:
                                    if len(entry) >= 5 and entry[1] in ["1", "2", "3"]:
                                        early_bs_entries.append(entry)
                                
                                if early_bs_entries:
                                    print(f"Found {len(early_bs_entries)} entries from minutes 1-3:")
                                    for entry in early_bs_entries[:3]:  # Show first 3 entries
                                        print(f"Raw entry: {entry}")
                                        print(f"Parsed as: Time: {entry[1]}, Over: {entry[2]}, Line: {entry[3]}, Under: {entry[4]}")
                                        print(f"Converted to American (Hong Kong odds): Time: {entry[1]}, "
                                              f"Over: {hk_to_american_str(entry[2])}, Line: {entry[3]}, Under: {hk_to_american_str(entry[4])}")
                                        print("-" * 40)
                                else:
                                    print("No early game BS entries found (minutes 1-3)")
                                    
                                    # Show pre-match entries instead
                                    pre_match = [entry for entry in bookmaker_data["bs"] 
                                                if len(entry) >= 5 and (not entry[1] or entry[1] == "")]
                                    if pre_match:
                                        print(f"Found {len(pre_match)} pre-match entries:")
                                        for entry in pre_match[:1]:  # Show just the first one
                                            print(f"Raw entry: {entry}")
                                            print(f"Parsed as: Time: pre-match, Over: {entry[2]}, Line: {entry[3]}, Under: {entry[4]}")
                                            print(f"Converted to American (Hong Kong odds): Time: pre-match, "
                                                  f"Over: {hk_to_american_str(entry[2])}, Line: {entry[3]}, Under: {hk_to_american_str(entry[4])}")
                                            print("-" * 40)
                                break
                    
                    # Format the match odds
                    formatted_odds = format_match_odds(odds_data)
                    
                    # Get environment data
                    environment = match_data.get("environment", {})
                    weather = environment.get("weather", "")
                    temperature = environment.get("temperature", "")
                    wind = environment.get("wind", "")
                    humidity = environment.get("humidity", "")
                    
                    # Convert temperature from Celsius to Fahrenheit if available
                    temperature_fahrenheit = ""
                    if temperature:
                        try:
                            temp_c = float(temperature)
                            temp_f = (temp_c * 9/5) + 32
                            temperature_fahrenheit = f"{temp_f:.1f}°F"
                        except (ValueError, TypeError):
                            temperature_fahrenheit = ""
                    
                    # Process weather code to text description
                    weather_text = get_weather_description(weather) if weather else ""
                    
                    # Convert wind speed from m/s to mph if available
                    wind_mph = ""
                    if wind:
                        try:
                            wind_mps = float(wind)
                            wind_mph = f"{wind_mps * 2.237:.1f} mph"
                        except (ValueError, TypeError):
                            wind_mph = wind
                    
                    # Format humidity with single %
                    humidity_text = ""
                    if humidity:
                        # Remove any existing % sign and add a single one
                        humidity_clean = str(humidity).replace("%", "").strip()
                        humidity_text = f"{humidity_clean}%"
                    
                    # Print match summary
                    print("\n----- MATCH SUMMARY -----")
                    print(f"Competition ID: {competition_id}")
                    print(f"Competition: {competition_name} ({competition_country})")
                    print(f"Match: {home_team_name} vs {away_team_name}")
                    print(f"Score: {match_data.get('home_score', 0)} - {match_data.get('away_score', 0)} (HT: {match_data.get('home_score_half', 0)} - {match_data.get('away_score_half', 0)})")
                    print(f"Status: {match_data.get('status_name', 'Unknown')}")
                    
                    # Print odds information first
                    if formatted_odds:
                        print("\n--- MATCH BETTING ODDS ---")
                        print(format_odds_display(formatted_odds))
                    
                    # Print environment info after the odds
                    if weather_text or temperature_fahrenheit or wind_mph or humidity_text:
                        print("\n--- MATCH ENVIRONMENT ---")
                        if weather_text:
                            print(f"Weather: {weather_text}")
                        if temperature_fahrenheit:
                            print(f"Temperature: {temperature_fahrenheit}")
                        if wind_mph:
                            print(f"Wind: {wind_mph}")
                        if humidity_text:
                            print(f"Humidity: {humidity_text}")
                    else:
                        print("\n--- MATCH ENVIRONMENT ---")
                        print("No environment data available for this match")
                    
                    print("-------------------------\n")
                except Exception as e:
                    print(f"Error processing match {match_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()
    except Exception as e:
        print(f"An error occurred in the main function: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
