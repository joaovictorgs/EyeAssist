# Backend-node

This is the central API and database manager for the EyeAssist project. It serves as the bridge between the physical Raspberry Pi sensors and the React frontend dashboard.

## Overview
Built with **Node.js**, **Express**, and **TypeScript**, this service:
- Exposes a REST API (`POST /readings`) to receive aggregated BLE tracking telemetry from the Main-Pi.
- Validates the incoming payload data structures.
- Saves historical tracking data into **MongoDB** using Mongoose.
- Serves the latest tracking data to the frontend via `GET /readings`.

## Setup & Run
1. Make sure MongoDB is installed and running locally on port 27017.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
The server will run on `http://localhost:3000`.