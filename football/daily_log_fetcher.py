#!/usr/bin/env python3
"""
Daily Log Fetcher for Live Football Data
Creates a daily log of all fetches made by live.py without modifying the original script
"""

import os
import sys
import time
import datetime
import subprocess
import json
import signal
import argparse
from pathlib import Path

# Configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LIVE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live.py")

def setup_logging_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created logs directory at {LOG_DIR}")

def get_log_filename():
    """Get log filename based on current date"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"football_fetches_{today}.log")

def log_fetch_data(log_file, data):
    """Log fetch data to the appropriate file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the log entry
    log_entry = {
        "timestamp": timestamp,
        "data": data
    }
    
    # Write to log file
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + "\n")

def parse_live_output(output, log_file):
    """Parse the output from live.py and extract relevant information"""
    # Extract match data
    matches = []
    current_match = {}
    in_match = False
    match_count = 0
    
    for line in output.split('\n'):
        if "===== FOUND " in line and "LIVE FOOTBALL MATCHES =====" in line:
            # Extract total matches count
            try:
                match_count = int(line.split("FOUND ")[1].split(" LIVE")[0])
            except:
                match_count = 0
                
        elif "MATCH #" in line and "OF" in line:
            # Start of a new match
            if current_match and in_match:
                matches.append(current_match)
            current_match = {"raw_header": line}
            in_match = True
            
        elif "----- MATCH SUMMARY -----" in line:
            current_match["section"] = "summary"
            
        elif "--- MATCH BETTING ODDS ---" in line:
            current_match["section"] = "odds"
            
        elif "--- MATCH ENVIRONMENT ---" in line:
            current_match["section"] = "environment"
            
        elif "Competition ID:" in line and in_match:
            try:
                current_match["competition_id"] = line.split("Competition ID:")[1].strip()
            except:
                pass
                
        elif "Competition:" in line and in_match:
            try:
                current_match["competition"] = line.split("Competition:")[1].strip()
            except:
                pass
                
        elif "Match:" in line and in_match:
            try:
                match_text = line.split("Match:")[1].strip()
                current_match["match"] = match_text
                # Try to extract teams
                if " vs " in match_text:
                    teams = match_text.split(" vs ")
                    current_match["home_team"] = teams[0].strip()
                    current_match["away_team"] = teams[1].strip()
            except:
                pass
                
        elif "Score:" in line and in_match:
            try:
                current_match["score"] = line.split("Score:")[1].strip()
            except:
                pass
                
        elif "Status:" in line and in_match:
            try:
                current_match["status"] = line.split("Status:")[1].strip()
            except:
                pass
                
        elif "Over/Under:" in line and in_match:
            try:
                current_match["ou_line"] = line.split("Line:")[1].split("|")[0].strip() if "Line:" in line else ""
            except:
                pass
    
    # Add the last match if there is one
    if current_match and in_match:
        matches.append(current_match)
    
    # Create the log data
    log_data = {
        "total_matches": match_count,
        "matches": matches
    }
    
    # Log the data
    log_fetch_data(log_file, log_data)
    
    return log_data

def run_live_and_log(interval=30, max_runs=None):
    """Run live.py and log its output periodically"""
    setup_logging_directory()
    log_file = get_log_filename()
    
    print(f"Starting daily logging of live.py fetches")
    print(f"Log file: {log_file}")
    print(f"Interval: {interval} seconds")
    if max_runs:
        print(f"Maximum runs: {max_runs}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    run_count = 0
    try:
        while True:
            # Get the current time for this run
            run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\nFetch #{run_count+1} at {run_time}")
            
            # Run live.py in non-continuous mode to get a single fetch
            cmd = [sys.executable, LIVE_SCRIPT]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                output = result.stdout
                
                # Parse and log the output
                log_data = parse_live_output(output, log_file)
                
                print(f"Logged {log_data['total_matches']} matches to {log_file}")
                
            except Exception as e:
                print(f"Error running live.py: {e}")
            
            # Increment run count
            run_count += 1
            
            # Check if we've reached the maximum number of runs
            if max_runs and run_count >= max_runs:
                print(f"Reached maximum number of runs ({max_runs}). Exiting.")
                break
                
            # Wait for the next interval
            next_time = (datetime.datetime.now() + datetime.timedelta(seconds=interval)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Next fetch at {next_time}")
            print("-" * 50)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    except Exception as e:
        print(f"Error in logging process: {e}")
    finally:
        print(f"\nLogging completed. Log file: {log_file}")
        print(f"Total fetches logged: {run_count}")

def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM signals"""
    print("\nLogging stopped by signal.")
    sys.exit(0)

def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Daily Log Fetcher for Live Football Data')
    parser.add_argument('-i', '--interval', type=int, default=30,
                        help='Interval between fetches in seconds (default: 30)')
    parser.add_argument('-m', '--max-runs', type=int, default=None,
                        help='Maximum number of fetches to log (default: unlimited)')
    args = parser.parse_args()
    
    # Run the logger
    run_live_and_log(interval=args.interval, max_runs=args.max_runs)

if __name__ == "__main__":
    main()
