import express from "express";
import { getDatabaseName, getMongoClient } from "./mongodb";

const app = express();
const port = 3000;

app.use(express.json());

type PiReadingPayload = {
  timestamp: number;
  datetime: string;
  device_id: string;
  measurements: {
    distance_to_satellite: number;
    distance_to_target: number;
  };
};

app.post("/readings", async (req, res) => {
  const body = req.body as Partial<PiReadingPayload>;

  if (
    typeof body.timestamp !== "number" ||
    typeof body.datetime !== "string" ||
    typeof body.device_id !== "string" ||
    !body.measurements ||
    typeof body.measurements.distance_to_satellite !== "number" ||
    typeof body.measurements.distance_to_target !== "number"
  ) {
    res.status(400).json({
      ok: false,
      error: "Invalid payload",
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
  console.log("server in http://localhost:" + port);
});
