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
import signal
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Configuration
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LIVE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live.py")

# Eastern Time zone offset (UTC-5 or UTC-4 during DST)
def get_eastern_time():
    """Get current datetime in US Eastern Time (handles DST)"""
    # Get UTC time
    utc_now = datetime.now(timezone.utc)
    
    # Eastern Standard Time is UTC-5
    # Eastern Daylight Time is UTC-4
    # Python can determine if DST is in effect
    est_offset = -5
    edt_offset = -4
    
    # Check if DST is in effect (approximate method)
    # DST in US starts second Sunday in March and ends first Sunday in November
    year = utc_now.year
    dst_start = datetime(year, 3, 8, 2, 0, tzinfo=timezone.utc)  # 2 AM on second Sunday in March
    dst_start += timedelta(days=(6 - dst_start.weekday()) % 7)  # Adjust to Sunday
    
    dst_end = datetime(year, 11, 1, 2, 0, tzinfo=timezone.utc)  # 2 AM on first Sunday in November
    dst_end += timedelta(days=(6 - dst_end.weekday()) % 7)  # Adjust to Sunday
    
    # Determine if we're in DST
    is_dst = dst_start <= utc_now < dst_end
    offset = edt_offset if is_dst else est_offset
    
    # Apply offset
    et = utc_now + timedelta(hours=offset)
    return et

def setup_logging_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created logs directory at {LOG_DIR}")

def get_log_filename():
    """Get log filename based on current date in Eastern Time"""
    today = get_eastern_time().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"football_fetches_{today}.log")

def log_raw_output(log_file, output):
    """Log the raw output from live.py exactly as it appears"""
    timestamp = get_eastern_time().strftime("%Y-%m-%d %H:%M:%S ET")
    
    # Write timestamp and separator
    with open(log_file, 'a') as f:
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write(f"FETCH TIMESTAMP: {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        
        # Write the raw output exactly as it appears
        f.write(output)
        
        # Add trailing separator
        f.write("\n" + "=" * 80 + "\n")

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
            run_time = get_eastern_time().strftime("%Y-%m-%d %H:%M:%S ET")
            print(f"\nFetch #{run_count+1} at {run_time}")
            
            # Run live.py in non-continuous mode to get a single fetch
            cmd = [sys.executable, LIVE_SCRIPT]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                output = result.stdout
                
                # Log the raw output
                log_raw_output(log_file, output)
                
                # Extract match count for feedback
                match_count = 0
                for line in output.split('\n'):
                    if "===== FOUND " in line and "LIVE FOOTBALL MATCHES =====" in line:
                        try:
                            match_count = int(line.split("FOUND ")[1].split(" LIVE")[0])
                        except:
                            match_count = 0
                            
                print(f"Logged {match_count} matches to {log_file}")
                
            except Exception as e:
                print(f"Error running live.py: {e}")
            
            # Increment run count
            run_count += 1
            
            # Check if we've reached the maximum number of runs
            if max_runs and run_count >= max_runs:
                print(f"Reached maximum number of runs ({max_runs}). Exiting.")
                break
                
            # Wait for the next interval
            next_time = (get_eastern_time() + timedelta(seconds=interval)).strftime("%Y-%m-%d %H:%M:%S ET")
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
