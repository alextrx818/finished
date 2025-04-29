from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_live_matches():
    """
    Fetch live football matches from the API
    """
    url = "https://api.thesports.com/v1/football/match/detail_live"
    params = {
        "user": "thenecpt",
        "secret": "0c55322e8e196d6ef9066fa4252cf386"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live matches: {e}")
        return {"error": str(e)}

@app.route('/api/matches', methods=['GET'])
def get_matches():
    matches_data = fetch_live_matches()
    return jsonify(matches_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
