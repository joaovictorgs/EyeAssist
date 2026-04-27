import { useEffect, useState } from "react";
import axios from "axios";

type PiReadingPayload = {
  _id: string;
  timestamp: number;
  datetime: string;
  device_id: string;
  measurements: {
    distance_to_satellite: number;
    distance_to_target: number;
  };
  received_at: string;
};

function App() {
  const [readings, setReadings] = useState<PiReadingPayload[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchReadings = async (isInitial = false) => {
    if (isInitial) setLoading(true);
    try {
      const response = await axios.get("http://localhost:3000/readings");
      if (response.data.ok) {
        setReadings(response.data.readings);
        setError(null);
      } else {
        setError("API Sent an Error");
      }
    } catch (err) {
      console.error(err);
      if (axios.isAxiosError(err)) {
        setError(err.message || "Error when connecting to the API");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unknow error when trying to connect to the API");
      }
    } finally {
      if (isInitial) setLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      await fetchReadings(true);
    };
    init();

    const interval = setInterval(() => fetchReadings(false), 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Reading Panel - EyeAssist</h1>

      {loading && readings.length === 0 && <p>Searching on the Backend...</p>}
      {error && <p>Erro: {error}</p>}

      <div>
        {readings.length > 0
          ? readings.map((r, i) => (
              <div key={r._id || i}>
                <p>
                  <strong>Device:</strong> {r.device_id} |{" "}
                  <strong>Time:</strong>{" "}
                  {new Date(r.received_at).toLocaleTimeString()} |{" "}
                  <strong>Dist. Target:</strong>{" "}
                  {r.measurements.distance_to_target} |{" "}
                  <strong>Dist. satellite :</strong>{" "}
                  {r.measurements.distance_to_satellite}
                </p>
                <hr />
              </div>
            ))
          : !loading && (
              <p>None readings found at the moment, verify the conection.</p>
            )}
      </div>
      <p>Update each 5 secconds.</p>
    </div>
  );
}

export default App;
