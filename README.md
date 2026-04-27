# EyeAssist: Indoor Navigation System

#### Student Name: _João Victor Godoy da Silva_

#### Student ID: _20119698_

## Project Description

This project proposes the development of a low-cost indoor positioning system using Bluetooth Low Energy (BLE) technology. The system will use multiple BLE beacons placed around the edges of a room to estimate the position of a user in real time.

A Raspberry Pi will act as the central processing unit, scanning BLE signals (RSSI - Received Signal Strength Indicator) to determine the user's approximate location. Instead of relying on precise triangulation, the system will use a zone-based approach, dividing the room into regions such as "safe area", "near wall", and "near obstacle".

A scaled digital map of the environment will be used as a reference. Based on the user's estimated position, the system will detect proximity to walls or obstacles and provide feedback through a vibration mechanism.

---

## Current Architecture & Data Flow

The system is split into multiple interconnected modules, working together to read physical device proximity, aggregate the data, persist it, and visualize it in real-time.

1. **BLE Device (Cellphone)**: Acts as the target beacon, transmitting BLE signals.
2. **Helper PI3 (`Helper-Pi/`)**:
   - Reads the RSSI from the target BLE device.
   - Sends this RSSI reading via an **MQTT** broker.
3. **Main PI4 (`Main-Pi/`)**:
   - Reads the RSSI directly from the BLE device.
   - Subscribes to the **MQTT** broker to receive the auxiliary RSSI readings from the Helper PI3.
   - Processes both signals, formats them into a standardized telemetry payload, and sends all readings to the backend via HTTP.
4. **Local Website Backend (`Backend-node/`)**:
   - A Node.js/Express server that receives the telemetry from the Main PI4.
   - **Reads/Writes** these payloads into a **MongoDB** database for historical tracking.
   - Exposes REST API endpoints (`GET /readings`) to fetch the data.
5. **User React App (`Front-React/`)**:
   - A React-based polling dashboard that reads the telemetry from the backend.
   - Processes the data to eventually display a visual heatmap of the user's real-time location.

---

## Tools, Technologies and Equipment

The following tools and technologies are proposed for this project:

### Hardware:

- **Main PI4** (Central aggregator & processor)
- **Helper PI3** (Secondary edge scanner)
- **BLE Device** (Target to track, e.g., a cellphone)
- Optional wearable device with:
  - Vibration motor or something for touch/hearing feedback
  - Accelerometer and/or gyroscope (for motion detection)

### Software & Stack:

- **Python**: Runs on the Raspberry Pis (`bluepy`/`bleak` for BLE, `paho-mqtt` for messaging).
- **MQTT**: Lightweight messaging protocol for Pi-to-Pi communication.
- **Node.js & Express**: Backend API server.
- **MongoDB**: NoSQL database for telemetry persistence.
- **React & TypeScript**: Frontend web application for data visualization (`Vite`).
