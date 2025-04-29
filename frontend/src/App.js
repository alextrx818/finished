import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [matches, setMatches] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('parsed'); // 'parsed', 'target', or 'raw'
  const [targetMatchId] = useState('y0or5jhnp844qwz');
  const [targetMatch, setTargetMatch] = useState(null);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/api/matches');
        setMatches(response.data);
        
        // Find the target match
        const targetId = 'y0or5jhnp844qwz';
        if (response.data && response.data.results) {
          const found = response.data.results.find(match => match.id === targetId);
          setTargetMatch(found || null);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Error fetching match data: ' + err.message);
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  const renderRawJson = () => {
    return (
      <div className="raw-json">
        <h2>Raw JSON Data</h2>
        <pre>{JSON.stringify(matches, null, 2)}</pre>
      </div>
    );
  };

  const renderTargetMatch = () => {
    if (!targetMatch) {
      return (
        <div className="no-target-match">
          <h2>Target Match Not Found</h2>
          <p>The match with ID "{targetMatchId}" was not found in the current data.</p>
        </div>
      );
    }

    // Extract score information
    const score = targetMatch.score || [];
    const statusCode = score[1] || "Unknown";
    const homeScores = score[2] || [];
    const awayScores = score[3] || [];
    const homeTotalScore = homeScores.reduce((a, b) => a + b, 0);
    const awayTotalScore = awayScores.reduce((a, b) => a + b, 0);

    // Extract stats information
    const stats = targetMatch.stats || [];
    
    // Map stat types to readable descriptions
    const statTypeMap = {
      2: "Corners",
      3: "Yellow Cards",
      4: "Red Cards",
      8: "Penalties",
      21: "Fouls",
      22: "Free Kicks",
      23: "Attacks",
      24: "Shots",
      25: "Possession (%)"
    };

    // Extract incidents
    const incidents = targetMatch.incidents || [];
    
    // Map incident types to readable descriptions
    const incidentTypeMap = {
      3: "🟨 Yellow Card",
      8: "🟥 Red Card",
      9: "🔄 Substitution",
      11: "⏱️ Half Time",
      12: "⏱️ Full Time",
      17: "⚽ Goal"
    };

    return (
      <div className="target-match">
        <div className="target-match-header">
          <h2>Target Match Found</h2>
          <div className="match-id">ID: {targetMatch.id}</div>
        </div>

        <div className="match-details">
          <div className="match-section">
            <h3>Score Information</h3>
            <div className="score-display highlight">
              <div className="team">
                <span className="team-name">Home Team</span>
                <span className="score">{homeTotalScore}</span>
              </div>
              <span className="vs">vs</span>
              <div className="team">
                <span className="team-name">Away Team</span>
                <span className="score">{awayTotalScore}</span>
              </div>
            </div>
            
            <table className="info-table">
              <thead>
                <tr>
                  <th>Detail</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Status Code</td>
                  <td>{statusCode === 2 ? "Live" : statusCode}</td>
                </tr>
                <tr>
                  <td>Home Score Details</td>
                  <td>{JSON.stringify(homeScores)}</td>
                </tr>
                <tr>
                  <td>Away Score Details</td>
                  <td>{JSON.stringify(awayScores)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {stats.length > 0 && (
            <div className="match-section">
              <h3>Match Statistics</h3>
              <table className="info-table">
                <thead>
                  <tr>
                    <th>Statistic</th>
                    <th>Home</th>
                    <th>Away</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.map((stat, index) => (
                    <tr key={index}>
                      <td>{statTypeMap[stat.type] || `Type ${stat.type}`}</td>
                      <td>{stat.home}</td>
                      <td>{stat.away}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {incidents.length > 0 && (
            <div className="match-section">
              <h3>Match Incidents</h3>
              <table className="info-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Type</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((incident, index) => (
                    <tr key={index}>
                      <td>{incident.time}'</td>
                      <td>{incidentTypeMap[incident.type] || `Type ${incident.type}`}</td>
                      <td>
                        {incident.player_name && `Player: ${incident.player_name}`}
                        {incident.in_player_name && `In: ${incident.in_player_name}, Out: ${incident.out_player_name}`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="match-section">
            <h3>Full Match JSON</h3>
            <pre className="match-json">{JSON.stringify(targetMatch, null, 2)}</pre>
          </div>
        </div>
      </div>
    );
  };

  const renderParsedMatches = () => {
    if (!matches || !matches.results || matches.results.length === 0) {
      return <p>No matches available</p>;
    }

    return (
      <div className="matches-container">
        <h2>Live Football Matches</h2>
        <div className="matches-grid">
          {matches.results.map((match) => {
            // Determine if this is the target match
            const isTargetMatch = match.id === targetMatchId;
            
            return (
              <div 
                key={match.id} 
                className={`match-card ${isTargetMatch ? 'highlight-match' : ''}`}
              >
                <h3>
                  Match ID: {match.id}
                  {isTargetMatch && <span className="target-badge">Target Match</span>}
                </h3>
                
                {match.score && (
                  <div className="score-info">
                    <p>Status: {match.score[1] === 2 ? 'Live' : 'Unknown'}</p>
                    
                    <div className="score-display">
                      <div className="team">
                        <span className="team-name">Home Team</span>
                        <span className="score">{match.score[2] && match.score[2].reduce((a, b) => a + b, 0)}</span>
                      </div>
                      <span className="vs">vs</span>
                      <div className="team">
                        <span className="team-name">Away Team</span>
                        <span className="score">{match.score[3] && match.score[3].reduce((a, b) => a + b, 0)}</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {match.stats && (
                  <div className="stats">
                    <h4>Match Statistics</h4>
                    <ul>
                      {match.stats.map((stat, i) => (
                        <li key={i}>
                          Type {stat.type}: Home {stat.home} - Away {stat.away}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {match.incidents && match.incidents.length > 0 && (
                  <div className="incidents">
                    <h4>Key Events</h4>
                    <ul>
                      {match.incidents.map((incident, i) => (
                        <li key={i}>
                          {incident.type === 17 ? '⚽ Goal' : 
                           incident.type === 3 ? '🟨 Yellow Card' : 
                           incident.type === 8 ? '🟥 Red Card' : 
                           incident.type === 9 ? '🔄 Substitution' : 
                           incident.type === 11 ? '⏱️ Half Time' : 
                           incident.type === 12 ? '⏱️ Full Time' : 
                           `Event Type ${incident.type}`} 
                          - Time: {incident.time}'
                          {incident.player_name && ` - Player: ${incident.player_name}`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Football Live Matches</h1>
        <div className="view-toggles">
          <button 
            className={viewMode === 'parsed' ? 'active' : ''} 
            onClick={() => setViewMode('parsed')}
          >
            All Matches
          </button>
          <button 
            className={viewMode === 'target' ? 'active' : ''} 
            onClick={() => setViewMode('target')}
          >
            Target Match (ID: {targetMatchId})
          </button>
          <button 
            className={viewMode === 'raw' ? 'active' : ''} 
            onClick={() => setViewMode('raw')}
          >
            Raw JSON
          </button>
        </div>
      </header>

      <main className="app-content">
        {loading ? (
          <div className="loading">Loading match data...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          viewMode === 'raw' ? renderRawJson() : 
          viewMode === 'target' ? renderTargetMatch() : 
          renderParsedMatches()
        )}
      </main>

      <footer className="app-footer">
        <p>Football Match Data powered by TheSports API</p>
      </footer>
    </div>
  );
}

export default App;
