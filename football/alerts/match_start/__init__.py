"""
Match Start Alerts Module
Contains alert criteria for events at the beginning of matches
"""

# Import all alert types for easier access
try:
    from .three_ou import ThreeOUStartAlert
except ImportError:
    pass  # Will be handled in main script
