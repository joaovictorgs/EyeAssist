import asyncio
import os
import math
from bleak import BleakScanner

#to get it the best way to is using the pi, if you know your device name, star a scan using
#bluetoothctl
#power on
#scan on
TARGET_MAC = "76:B6:B7:E9:33:98"

#value that your device sends when 1m at the pi
CALIBRATION_1M_RSSI = -80

# external factor
ENVIRONMENT_FACTOR = 2.0 # between 2 or 3 for enclose spaces
SMOOTHING_SAMPLES = 5    # quantity of samples for mesure average and median

def calculate_distance(rssi):
    # d = 10 ^ ((TxPower - RSSI) / (10 * N))
    distance = 10 ** ((CALIBRATION_1M_RSSI - rssi) / (10 * ENVIRONMENT_FACTOR))
    return round(distance, 2)

def clear_console():
    os.system('clear')

async def main():
    recent_readings = [] # list of recent readings

    #function to read only the device that is tagged as TARGET_MAC
    def detection_callback(device, advertisement_data):
        mac = device.address.upper()
        if mac == TARGET_MAC:
            recent_readings.append(advertisement_data.rssi)
            if len(recent_readings) > SMOOTHING_SAMPLES:
                recent_readings.pop(0)

    scanner = BleakScanner(detection_callback)
    await scanner.start()
    
    try:
        while True:
            #async sleep to not break the scanner
            await asyncio.sleep(1.0) 
            
            clear_console()
            print("last reading | Average | Estimed distance")
            print("-" *42)
            
            if recent_readings:
                # calculate the average RSSi
                avg_rssi = sum(recent_readings) / len(recent_readings)
                latest_rssi = recent_readings[-1]
                
                # calculate the distance using the average reading
                estimated_distance = calculate_distance(avg_rssi)
                
                print(f"{latest_rssi:<13}|{round(avg_rssi, 1):<9}|{estimated_distance} meters")
            else:
                print("awaiting for device to start sending RSSI signal")
    #exception to when the user presses ctrl+c on the terminal
    except asyncio.CancelledError:
        pass
    finally:
        await scanner.stop()
        print("\nending scanning.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
