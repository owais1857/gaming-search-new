import React, { useState } from 'react';
import './App.css';

function App() {
  // State variables to store user input and results
  const [query, setQuery] = useState('');
  const [role, setRole] = useState('gamer'); // Default role
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle the search request
  const handleSearch = async (e) => {
    e.preventDefault(); // Prevent form from reloading the page
    setIsLoading(true);
    setResults([]);

    try {
      // Send the query and role to our Flask backend API
      const response = await fetch('http://localhost:5001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, role }),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Failed to fetch search results:", error);
      // You could add error handling here, e.g., setResults([{title: 'Error fetching results'}]);
    }

    setIsLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Personalized Gaming Search</h1>
        <p className="privacy-notice">We don’t log your searches. No ads, no trackers.</p>
      </header>

      <form className="search-form" onSubmit={handleSearch}>
        <select value={role} onChange={(e) => setRole(e.target.value)} className="role-selector">
          <option value="gamer">Gamer</option>
          <option value="developer">Developer</option>
        </select>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for news, guides, jobs..."
          className="search-input"
        />
        <button type="submit" className="search-button">Search</button>
      </form>

      <div className="results-container">
        {isLoading && <p>Loading...</p>}
        {results.map((result, index) => (
          <div key={index} className="result-item">
            <h3>
              <a href={result.url} target="_blank" rel="noopener noreferrer">
                {result.title}
              </a>
            </h3>
            <p className="result-source">Source: {result.source}</p>
            <p className="result-summary">{result.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;