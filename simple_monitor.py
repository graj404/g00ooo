#!/usr/bin/env python3
"""
Simple Vehicle Monitor - Matches your working code
Displays: Speed, Heading, Turn Radius, Fuel, Distance
Uses: IR sensor, AS5600 angle sensor, ADS1115 fuel sensor
"""

import time
import threading
import math
from gpiozero import DigitalInputDevice
from smbus2 import SMBus
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# -------------------- CONSTANTS --------------------
WHEEL_DIAMETER = 0.275  # meters
WHEEL_BASE = 1.2        # meters
MIN_VOLTAGE = 0.04
MAX_VOLTAGE = 0.7

# -------------------- IR SENSOR --------------------
sensor = DigitalInputDevice(27, pull_up=False)
count = 0
last_state = 0
rps = 0

# -------------------- ANGLE SENSOR --------------------
I2C_ADDR = 0x36
bus = SMBus(1)
angle = 0

# -------------------- DISTANCE --------------------
distance = 0
last_time = time.time()

# -------------------- ADC --------------------
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, 0)

# -------------------- RPM THREAD --------------------
def rpm_counter():
    global count, last_state, rps
    start_time = time.time()
    
    while True:
        current_state = sensor.value
        
        if current_state == 1 and last_state == 0:
            count += 1
        
        last_state = current_state
        
        if time.time() - start_time >= 1:
            rps = count
            count = 0
            start_time = time.time()

# -------------------- ANGLE THREAD --------------------
def angle_reader():
    global angle
    
    while True:
        try:
            data = bus.read_i2c_block_data(I2C_ADDR, 0x0C, 2)
            raw = (data[0] << 8) | data[1]
            angle = (raw / 4096.0) * 360.0
        except:
            angle = 0
        
        time.sleep(0.05)

# Start threads
threading.Thread(target=rpm_counter, daemon=True).start()
threading.Thread(target=angle_reader, daemon=True).start()

# -------------------- MAIN LOOP --------------------
print("Vehicle Monitor Started")
print("Press Ctrl+C to stop")
print("-" * 50)

try:
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # -------- SPEED --------
        circumference = math.pi * WHEEL_DIAMETER
        speed_mps = rps * circumference
        speed_kmph = speed_mps * 3.6
        
        # -------- TURN RADIUS --------
        theta_rad = math.radians(angle)
        if abs(theta_rad) < 0.01:
            radius_text = "∞"
        else:
            radius = WHEEL_BASE / math.tan(theta_rad)
            radius_text = f"{radius:.2f} m"
        
        # -------- DISTANCE (Dead Reckoning) --------
        distance += speed_mps * dt
        
        # -------- FUEL --------
        voltage = chan.voltage
        fuel = ((voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)) * 100
        fuel = 100 - fuel
        fuel = max(0, min(100, fuel))
        
        # -------- DISPLAY --------
        print(f"\rSpeed: {speed_kmph:6.2f} km/h | "
              f"Heading: {angle:6.2f}° | "
              f"Radius: {radius_text:>8} | "
              f"Fuel: {fuel:5.1f}% | "
              f"Distance: {distance:7.2f} m", end='')
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nStopping monitor...")
    sensor.close()
    bus.close()
    print("Done!")
