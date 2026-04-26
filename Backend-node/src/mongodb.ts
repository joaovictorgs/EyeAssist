import { MongoClient } from "mongodb";

const mongoUri =
  process.env.MONGODB_URI ?? "mongodb://127.0.0.1:27017/eyeassist";
const client = new MongoClient(mongoUri);
const dbName = process.env.MONGODB_DB ?? "eyeassist";

let connectPromise: Promise<MongoClient> | null = null;

export async function getMongoClient(): Promise<MongoClient> {
  if (!connectPromise) {
    connectPromise = client.connect();
  }

  return connectPromise;
}

export function getDatabaseName(): string {
  return dbName;
}
