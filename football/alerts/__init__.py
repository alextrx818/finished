"""
Football Alerts Module
Contains custom alert criteria for the Football Alerts System
"""

# Import all alert types for easier access
try:
    from .HighLineHalftimeZero import HighLineHalftimeZeroAlert
    from .ThreeHtZero import ThreeHtZeroAlert
    from .match_start.three_ou import ThreeOUStartAlert
except ImportError:
    pass  # Will be handled in main script
