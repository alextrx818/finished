# Football Live Data Script (live.py)

## Overview
This script fetches and displays live football match data including match details, team information, competition data, and betting odds from TheSports API. It supports parallel processing for optimized performance and implements specific filtering rules for different types of odds.

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `https://api.thesports.com/v1/football/match/detail_live` | Fetches live match data |
| `https://api.thesports.com/v1/football/match/recent/list` | Fetches detailed match information |
| `https://api.thesports.com/v1/football/team/additional/list` | Fetches team information |
| `https://api.thesports.com/v1/football/competition/additional/list` | Fetches competition information |
| `https://api.thesports.com/v1/football/country/list` | Fetches country information |
| `https://api.thesports.com/v1/football/odds/history` | Fetches odds history data |

## API Credentials
- User: `thenecpt`
- Secret: `0c55322e8e196d6ef9066fa4252cf386`

## Odds Filtering Rules

All odds types (European, Asia Handicap, and Over/Under) are filtered to only include data from match minutes 4-6. If no data is available from these minutes, the script will fall back to using other available data.

### European (Money Line) Odds
- **Source field**: `eu` in odds data
- **Default bookmaker**: Bookmaker ID 2
- **Priority time window**: Minutes 4-6 of the match
- **Conversion**: Decimal odds to American odds
- **Format**: Standard American odds with +/- signs (e.g., `-150`, `+240`)

### Asia Handicap (SPREAD) Odds
- **Source field**: `asia` in odds data
- **Priority time window**: Minutes 4-6 of the match
- **Conversion**: Hong Kong odds to American odds
- **Format**: Standard American odds with +/- signs (e.g., `-110`, `+120`)

### Big Small (Over/Under) Odds
- **Source field**: `bs` in odds data
- **Priority time window**: Minutes 4-6 of the match
- **Conversion**: Hong Kong odds to American odds
- **Format**: Standard American odds with +/- signs (e.g., `-110`, `+120`)

## Odds Conversion Formulas

### Decimal to American Odds (European/Money Line)
- For decimal odds ≥ 2.0: `(decimal - 1) * 100` (with + sign)
- For decimal odds < 2.0: `-100 / (decimal - 1)` (with - sign)

### Hong Kong to American Odds (SPREAD and Over/Under)
- For Hong Kong odds ≥ 1.0: `odds * 100` (with + sign)
- For Hong Kong odds < 1.0: `-100 / odds` (with - sign)

## Output Display
The script outputs a formatted summary for each match including:
- Match teams and score
- Competition name and country
- Match environment (weather, temperature, wind, humidity)
- Betting odds in American format with proper +/- signs for:
  - SPREAD (Asia Handicap)
  - ML (Money Line)
  - Over/Under

## Command Line Usage
```bash
python football/live.py [number_of_matches]
```

Where `[number_of_matches]` is an optional parameter to limit the number of matches processed (default: 5).

## Performance Optimizations
- Uses concurrent.futures.ThreadPoolExecutor for parallel API requests
- Implements LRU caching with functools.lru_cache to minimize duplicate API calls
- Uses a single session for all HTTP requests to improve connection efficiency

## Error Handling
- Gracefully handles missing or invalid data fields
- Provides detailed debug output for odds conversion
- Implements proper exception handling and diagnostic information
