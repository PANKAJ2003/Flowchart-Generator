import React, { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // New state for loading
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setImgUrl("");
    setLoading(true); // Set loading to true when the flowchart generation starts
    
    try {
      const apiUrl = process.env.REACT_APP_API_URL;
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (response.ok) {
        setImgUrl(data.img_url);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false); // Set loading to false once the request is completed
    }
  };

  const downloadImage = () => {
    const link = document.createElement("a");
    link.href = imgUrl;
    link.download = "flowchart.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="App">
      <div className="container">
        <div className="left">
          <h1>Create Your Flowchart</h1>
          <form onSubmit={handleSubmit}>
            <input
              className="searchArea"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query"
            />
            <button className="generateButton" type="submit">
              Generate Flowchart
            </button>
          </form>
        </div>
        <div className="right">
          {error && <p className="error">{error}</p>}
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Generating your flowchart...</p>
            </div>
          ) : imgUrl ? (
            <>
              <h3>Generated Flowchart</h3>
              <div className="flowchart">
                <img src={imgUrl} alt="Generated flowchart" />
              </div>
              <button className="downloadButton" onClick={downloadImage}>
                Download Flowchart
              </button>
            </>
          ) : (
            <p>Your generated flowchart will appear here.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
