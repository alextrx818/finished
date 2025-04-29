#!/usr/bin/env python3
"""
Daily Log Viewer for Live Football Data
Analyze and display logs created by daily_log_fetcher.py
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

def get_available_logs():
    """Get a list of available log files"""
    if not os.path.exists(LOG_DIR):
        return []
        
    log_files = [f for f in os.listdir(LOG_DIR) if f.startswith("football_fetches_") and f.endswith(".log")]
    log_files.sort(reverse=True)  # Sort by date, newest first
    return log_files

def parse_log_file(log_file):
    """Parse a log file and return the fetch data"""
    full_path = os.path.join(LOG_DIR, log_file)
    fetches = []
    
    try:
        with open(full_path, 'r') as f:
            for line in f:
                try:
                    fetch_data = json.loads(line.strip())
                    fetches.append(fetch_data)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse line in {log_file}")
                    continue
    except Exception as e:
        print(f"Error reading log file {log_file}: {e}")
        return []
        
    return fetches

def analyze_log(fetches):
    """Analyze the log data and generate statistics"""
    stats = {
        "total_fetches": len(fetches),
        "total_matches": 0,
        "matches_by_competition": defaultdict(int),
        "matches_by_status": defaultdict(int),
        "matches_by_ou_line": defaultdict(int),
        "first_fetch_time": None,
        "last_fetch_time": None
    }
    
    # Track unique matches
    unique_matches = set()
    
    for fetch in fetches:
        # Update fetch times
        try:
            fetch_time = fetch["timestamp"]
            if stats["first_fetch_time"] is None or fetch_time < stats["first_fetch_time"]:
                stats["first_fetch_time"] = fetch_time
            if stats["last_fetch_time"] is None or fetch_time > stats["last_fetch_time"]:
                stats["last_fetch_time"] = fetch_time
        except KeyError:
            pass
            
        # Process match data
        try:
            fetch_data = fetch["data"]
            stats["total_matches"] += fetch_data.get("total_matches", 0)
            
            # Process each match
            for match in fetch_data.get("matches", []):
                # Create a unique identifier for the match
                if "home_team" in match and "away_team" in match:
                    match_id = f"{match['home_team']} vs {match['away_team']}"
                    unique_matches.add(match_id)
                
                # Count by competition
                if "competition" in match:
                    stats["matches_by_competition"][match["competition"]] += 1
                    
                # Count by status
                if "status" in match:
                    stats["matches_by_status"][match["status"]] += 1
                
                # Count by O/U line
                if "ou_line" in match and match["ou_line"]:
                    stats["matches_by_ou_line"][match["ou_line"]] += 1
        except KeyError:
            pass
    
    # Add unique match count
    stats["unique_matches"] = len(unique_matches)
    
    return stats

def display_fetch_summary(fetch):
    """Display a summary of a single fetch"""
    print(f"Fetch at: {fetch['timestamp']}")
    print(f"Total matches: {fetch['data'].get('total_matches', 0)}")
    print(f"Matches in this fetch:")
    
    for match in fetch['data'].get('matches', []):
        print(f"  - {match.get('match', 'Unknown Match')} | Status: {match.get('status', 'Unknown')}")
        if "ou_line" in match and match["ou_line"]:
            print(f"    O/U Line: {match['ou_line']}")
    print("-" * 50)

def display_log_stats(stats):
    """Display log statistics"""
    print("\n" + "=" * 50)
    print("DAILY LOG SUMMARY")
    print("=" * 50)
    print(f"Period: {stats['first_fetch_time']} to {stats['last_fetch_time']}")
    print(f"Total fetches: {stats['total_fetches']}")
    print(f"Total matches processed: {stats['total_matches']}")
    print(f"Unique matches: {stats['unique_matches']}")
    
    print("\nMatches by Competition:")
    for comp, count in sorted(stats["matches_by_competition"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {comp}: {count}")
        
    print("\nMatches by Status:")
    for status, count in sorted(stats["matches_by_status"].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {status}: {count}")
        
    print("\nMatches by O/U Line:")
    for line, count in sorted(stats["matches_by_ou_line"].items(), key=lambda x: float(x[0]) if x[0].replace('.', '', 1).isdigit() else 0, reverse=True):
        print(f"  - {line}: {count}")
    
    print("=" * 50)

def view_log(log_file, detailed=False):
    """View and analyze a log file"""
    print(f"Viewing log file: {log_file}")
    fetches = parse_log_file(log_file)
    
    if not fetches:
        print("No fetch data found in the log.")
        return
        
    print(f"Found {len(fetches)} fetches in the log.")
    
    # Display detailed fetch information if requested
    if detailed:
        print("\n" + "=" * 50)
        print("DETAILED FETCH INFORMATION")
        print("=" * 50)
        for fetch in fetches:
            display_fetch_summary(fetch)
    
    # Analyze and display statistics
    stats = analyze_log(fetches)
    display_log_stats(stats)

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Daily Log Viewer for Live Football Data')
    parser.add_argument('-d', '--date', type=str, default=None,
                        help='Date to view logs for (YYYY-MM-DD, default: today)')
    parser.add_argument('--detailed', action='store_true',
                        help='Show detailed information for each fetch')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List available log files')
    args = parser.parse_args()
    
    # List available log files if requested
    if args.list:
        log_files = get_available_logs()
        if log_files:
            print("Available log files:")
            for log_file in log_files:
                print(f"  - {log_file}")
        else:
            print("No log files found.")
        return
    
    # Determine which log file to view
    log_date = args.date
    if not log_date:
        log_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
    log_file = f"football_fetches_{log_date}.log"
    
    if not os.path.exists(os.path.join(LOG_DIR, log_file)):
        print(f"Log file for {log_date} not found.")
        log_files = get_available_logs()
        if log_files:
            print("\nAvailable log files:")
            for log_file in log_files:
                print(f"  - {log_file}")
        else:
            print("No log files found.")
        return
    
    # View the log
    view_log(log_file, detailed=args.detailed)

if __name__ == "__main__":
    main()
