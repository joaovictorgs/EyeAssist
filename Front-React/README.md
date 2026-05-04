# Front-React

This is the user interface for the EyeAssist project, displaying the real-time tracking data of the target device.

## Overview
Built with **React**, **Vite**, and **TypeScript**, this application provides a lightweight, credible academic dashboard:
- **Polling:** Automatically queries the `Backend-node` (`GET /readings`) every 5 seconds.
- **Data Visualization:** Displays a slider mapping the 0.0 to 1.0 position ratio onto the physical 3-meter distance between the Main-Pi and Helper-Pi.
- **Telemetry:** Renders raw data (MAC addresses, exact RSSI in dBm, and distance in meters) for auditing and transparency.

## Setup & Run
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```
The application will usually run on `http://localhost:5173`.