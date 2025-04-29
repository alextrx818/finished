#!/usr/bin/env python3
"""
Continuous Runner for Live Football Data
This script will run the live.py script every 30 seconds 
to continuously fetch and update football match data.
"""

import os
import sys
import time
import subprocess
import datetime
import signal
import argparse
import re
import tempfile

# Path to the live.py script (relative to this script)
LIVE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live.py")

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit gracefully"""
    print("\nExiting continuous fetch mode...")
    sys.exit(0)

def extract_match_data(output):
    """Extract only the essential match data from live.py output"""
    # Split the output by match
    matches = []
    match_count = 0
    
    # Find all match headers
    match_blocks = re.findall(r'={30}\nMATCH \d+ of \d+\n={30}.*?(?=={30}|\Z)', output, re.DOTALL)
    
    for match_block in match_blocks:
        # Extract the essential information
        match_summary = re.search(r'----- MATCH SUMMARY -----\n(.*?)(?=---|\Z)', match_block, re.DOTALL)
        betting_odds = re.search(r'--- MATCH BETTING ODDS ---\n(.*?)(?=---|\Z)', match_block, re.DOTALL)
        environment = re.search(r'--- MATCH ENVIRONMENT ---\n(.*?)(?=---|\Z)', match_block, re.DOTALL)
        
        if match_summary:
            match_count += 1
            summary_text = match_summary.group(1).strip()
            odds_text = betting_odds.group(1).strip() if betting_odds else "No betting odds available"
            env_text = environment.group(1).strip() if environment else "No environment data available"
            
            match_data = f"MATCH #{match_count}\n"
            match_data += "-" * 30 + "\n"
            match_data += summary_text + "\n\n"
            match_data += "--- MATCH BETTING ODDS ---\n" + odds_text + "\n\n"
            match_data += "--- MATCH ENVIRONMENT ---\n" + env_text
            matches.append(match_data)
    
    return matches, match_count

def run_live_script():
    """Run the live.py script and extract only the essential data"""
    try:
        # Clear the screen (works on both Windows and Unix-like systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Use a temp file to capture output
        with tempfile.TemporaryFile(mode='w+') as temp_output:
            # Run the live.py script with a large number to process all matches
            # We use 1000 to effectively have no limit without modifying live.py
            process = subprocess.run(
                [sys.executable, LIVE_SCRIPT, "1000"], 
                stdout=temp_output, 
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Go back to the beginning of the file
            temp_output.seek(0)
            
            # Read all output
            output = temp_output.read()
        
        # Extract match count from the output
        match_count_match = re.search(r'Found (\d+) live matches', output)
        total_matches = int(match_count_match.group(1)) if match_count_match else 0
        
        # Extract only the essential match data
        matches, processed_count = extract_match_data(output)
        
        # Print timestamp and match count
        print(f"=== FETCH @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"TOTAL LIVE MATCHES: {total_matches}")
        print(f"PROCESSED MATCHES: {processed_count}")
        print("=" * 50 + "\n")
        
        # Print each match's data
        for match in matches:
            print(match)
            print("\n" + "=" * 50 + "\n")
            
        if process.returncode != 0:
            print(f"Warning: live.py exited with code {process.returncode}")
            
    except Exception as e:
        print(f"Error running live.py: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run live.py continuously")
    parser.add_argument("--interval", type=int, default=30,
                      help="Interval between fetches in seconds (default: 30)")
    args = parser.parse_args()
    
    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"Starting continuous fetch mode (Press Ctrl+C to exit)")
    print(f"Fetching every {args.interval} seconds")
    print(f"Processing ALL available matches")
    
    # Main loop
    while True:
        try:
            # Run the live.py script
            run_live_script()
            
            # Wait for the specified interval
            print(f"\nNext fetch in {args.interval} seconds... (Press Ctrl+C to exit)")
            time.sleep(args.interval)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print("Continuing in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()
