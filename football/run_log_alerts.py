#!/usr/bin/env python3
"""
Main Log Scanner Entry Point
"""

import sys
import argparse
from log_alerts.scanner import main as scanner_main

if __name__ == "__main__":
    scanner_main()
