import express from "express";
import cors from "cors";
import { getDatabaseName, getMongoClient } from "./mongodb";

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
type AnchorReading = {
  name: string;
  distance: number;
  rssi: number;
};

type PiReadingPayload = {
  timestamp_sync: number;
  target_mac: string;
  anchors: AnchorReading[];
  estimated_position_ratio: number;
  estimated_position_meters: number;
  status: string;
};

function isValidPayload(body: any): body is PiReadingPayload {
  if (
    !body ||
    typeof body.timestamp_sync !== "number" ||
    typeof body.target_mac !== "string" ||
    typeof body.estimated_position_ratio !== "number" ||
    typeof body.estimated_position_meters !== "number" ||
    typeof body.status !== "string" ||
    !Array.isArray(body.anchors)
  ) {
    return false;
  }

  // Validate each anchor in the array
  for (const anchor of body.anchors) {
    if (
      typeof anchor.name !== "string" ||
      typeof anchor.distance !== "number" ||
      typeof anchor.rssi !== "number"
    ) {
      return false;
    }
  }

  return true;
}

app.post("/readings", async (req, res) => {
  const body = req.body;

  if (!isValidPayload(body)) {
    res.status(400).json({
      ok: false,
      error: "Invalid payload format. Please check required fields.",
    });
    return;
  }

  try {
    const client = await getMongoClient();
    const databaseName = getDatabaseName();
    const collection = client.db(databaseName).collection("pi_readings");

    const result = await collection.insertOne({
      ...body,
      received_at: new Date(),
    });

    res.status(201).json({
      ok: true,
      insertedId: result.insertedId,
    });
  } catch (error) {
    console.error("Failed to insert Pi reading:", error);
    const message =
      error instanceof Error ? error.message : "Unknown MongoDB error";
    res.status(500).json({ ok: false, error: message });
  }
});

app.get("/readings", async (req, res) => {
  try {
    const client = await getMongoClient();
    const databaseName = getDatabaseName();
    const collection = client.db(databaseName).collection("pi_readings");

    let query = {};

    if (req.query.seconds) {
      const seconds = parseInt(req.query.seconds as string, 10);

      if (!isNaN(seconds)) {
        const cutoffTime = new Date(Date.now() - seconds * 1000);
        query = { received_at: { $gte: cutoffTime } };
      }
    }

    const readings = await collection
      .find(query)
      .sort({ received_at: 1 })
      .toArray();

    res.json({
      ok: true,
      count: readings.length,
      readings: readings,
    });
  } catch (error) {
    console.error("Failed to fetch Pi readings:", error);
    const message =
      error instanceof Error ? error.message : "Unknown MongoDB error";
    res.status(500).json({ ok: false, error: message });
  }
});

app.get("/", (req, res) => {
  res.send("Get route");
});

app.post("/", (req, res) => {
  res.status(400).json({
    ok: false,
    error: "Use POST /readings with the Pi payload",
  });
});

app.get("/health", (req, res) => {
  res.json({ ok: true });
});

app.get("/mongo-health", async (req, res) => {
  try {
    const client = await getMongoClient();
    const databaseName = getDatabaseName();
    const result = await client.db(databaseName).command({ ping: 1 });

    res.json({ ok: true, database: databaseName, mongo: result });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown MongoDB error";
    res.status(500).json({ ok: false, error: message });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
