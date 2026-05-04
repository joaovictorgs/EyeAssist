import { useEffect, useState } from "react";
import axios from "axios";

type AnchorReading = {
  name: string;
  distance: number;
  rssi: number;
};

type AggregatedReading = {
  _id: string;
  timestamp_sync: number;
  target_mac: string;
  anchors: AnchorReading[];
  estimated_position_ratio: number;
  estimated_position_meters: number;
  status: string;
  received_at: string;
};

function App() {
  const [readings, setReadings] = useState<AggregatedReading[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchReadings = async () => {
    try {
      const response = await axios.get("http://localhost:3000/readings");
      if (response.data.ok) {
        setReadings(response.data.readings);
        setError(null);
      } else {
        setError("API Error.");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.message || "Failed to reach the API / DB.");
      } else {
        setError("Unknown Error.");
      }
    }
  };

  useEffect(() => {
    fetchReadings();
    const interval = setInterval(fetchReadings, 5000);
    return () => clearInterval(interval);
  }, []);

  const latestReading = readings.length > 0 ? readings[readings.length - 1] : null;

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif", maxWidth: "800px" }}>
      <h1>Dashboard - EyeAssist Project</h1>
      <p>Real-time location monitoring between Raspberry Pi anchors and the target device.</p>

      {error && (
        <div style={{ padding: "10px", border: "1px solid red", background: "#fdd", color: "red", marginBottom: "20px" }}>
          <b>Error:</b> {error}
        </div>
      )}

      {latestReading ? (
        <div>
          {/* Section 1: Simple Slider Visualization */}
          <div style={{ border: "2px solid black", padding: "20px", background: "#f4f4f4", marginBottom: "20px" }}>
            <h3>Estimated Target Position</h3>
            
            <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "20px 0" }}>
              <span><b>Main Pi</b> (0m)</span>
              
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={(latestReading.estimated_position_ratio * 100).toFixed(0)} 
                disabled 
                style={{ width: "400px" }} 
              />
              
              <span><b>Helper Pi</b> (3m)</span>
            </div>
            
            <p>
              Distance calculation: Target is approximately <b style={{color: "blue"}}>{Number(latestReading.estimated_position_meters).toFixed(2)} meters</b> from the Main Pi.<br/><br/>
              <small>(This represents {(latestReading.estimated_position_ratio * 100).toFixed(0)}% of the path towards the Helper Pi).</small>
            </p>
          </div>

          {/* Section 2: Raw MongoDB Data */}
          <div style={{ border: "1px solid gray", padding: "15px", background: "#fff" }}>
            <h4 style={{marginTop: 0}}>Latest Payload Received:</h4>
            
            <ul style={{ listStyleType: "none", paddingLeft: 0 }}>
              <li><b>Database Timestamp:</b> {new Date(latestReading.received_at).toLocaleString()}</li>
              <li><b>Status:</b> {latestReading.status}</li>
              <li><b>Target MAC Address:</b> {latestReading.target_mac}</li>
            </ul>

            <h4>Raw Anchor Readings:</h4>
            <table border={1} cellPadding={8} style={{ borderCollapse: "collapse", width: "100%", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#eee" }}>
                  <th>Anchor Pi</th>
                  <th>RSSI Signal (dBm)</th>
                  <th>Calculated Distance (m)</th>
                </tr>
              </thead>
              <tbody>
                {latestReading.anchors.map((anchor, idx) => (
                  <tr key={idx}>
                    <td>{anchor.name}</td>
                    <td>{anchor.rssi}</td>
                    <td>{anchor.distance.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <p style={{ color: "gray" }}>Waiting for Raspberry Pi data. Please ensure the Python scripts are running.</p>
      )}
    </div>
  );
}

export default App;
