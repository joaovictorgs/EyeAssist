# EyeAssist: Indoor Navigation System

#### Student Name: _João Victor Godoy da Silva_

#### Student ID: _20119698_

## Project Description

This project proposes the development of a low-cost indoor positioning system using Bluetooth Low Energy (BLE) technology. The system will use multiple BLE beacons placed around the edges of a room to estimate the position of a user in real time.

A Raspberry Pi will act as the central processing unit, scanning BLE signals (RSSI - Received Signal Strength Indicator) to determine the user's approximate location. Instead of relying on precise triangulation, the system will use a zone-based approach, dividing the room into regions such as "safe area", "near wall", and "near obstacle".

A scaled digital map of the environment will be used as a reference. Based on the user's estimated position, the system will detect proximity to walls or obstacles and provide feedback through a vibration mechanism.

Additionally, an accelerometer may be used to detect movement and improve the stability of the position estimation by reducing noise from signal fluctuations.

The main goal of this project is to create a simple and effective system for indoor navigation and collision avoidance, which could be extended to assistive technologies or smart environments.

---

## Tools, Technologies and Equipment

The following tools and technologies are proposed for this project:

### Hardware:

- Raspberry Pi (central processing unit)
- Multiple Raspberry Pi devices or BLE beacons (used as signal transmitters)
- Optional wearable device with:
  - Vibration motor or something that can have a response for the touch or hearing (for feedback)
  - Accelerometer and/or giroscope (for motion detection)

### Software:

- Python (main programming language)
- BLE libraries (`bluepy`, `bleak`, or similar)
- Data processing and signal analysis (RSSI handling)
- Simple mapping system (grid-based or image-based)

### Other:

- Scaled map of the room (digital representation)
- Calibration setup for RSSI measurement
