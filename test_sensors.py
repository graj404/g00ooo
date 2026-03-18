#!/usr/bin/env python3
"""
Test script for IR sensor and fuel sensor
Run this to verify sensor connections
"""

import time
from sensors import IRSensor, FuelSensor

def test_ir_sensor():
    """Test IR sensor"""
    print("Testing IR Sensor...")
    print("Spin the wheel to see RPM readings")
    print("Press Ctrl+C to stop\n")
    
    ir_sensor = IRSensor()
    
    try:
        while True:
            rpm = ir_sensor.get_rpm()
            rps = ir_sensor.get_rps()
            print(f"RPM: {rpm:.1f} | RPS: {rps:.1f}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping IR sensor test...")
        ir_sensor.cleanup()

def test_fuel_sensor():
    """Test fuel sensor"""
    print("\nTesting Fuel Sensor...")
    print("Reading fuel level from ADC")
    print("Press Ctrl+C to stop\n")
    
    fuel_sensor = FuelSensor()
    
    try:
        while True:
            fuel_level = fuel_sensor.read_fuel_level()
            voltage = fuel_sensor.get_voltage()
            print(f"Fuel: {fuel_level:.1f}% | Voltage: {voltage:.3f}V", end='\r')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping fuel sensor test...")

def test_both():
    """Test both sensors simultaneously"""
    print("Testing Both Sensors...")
    print("Press Ctrl+C to stop\n")
    
    ir_sensor = IRSensor()
    fuel_sensor = FuelSensor()
    
    try:
        while True:
            rpm = ir_sensor.get_rpm()
            fuel_level = fuel_sensor.read_fuel_level()
            voltage = fuel_sensor.get_voltage()
            
            print(f"RPM: {rpm:.1f} | Fuel: {fuel_level:.1f}% ({voltage:.3f}V)", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping sensor tests...")
        ir_sensor.cleanup()

if __name__ == "__main__":
    print("Sensor Test Menu")
    print("1. Test IR Sensor only")
    print("2. Test Fuel Sensor only")
    print("3. Test both sensors")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == "1":
        test_ir_sensor()
    elif choice == "2":
        test_fuel_sensor()
    elif choice == "3":
        test_both()
    else:
        print("Invalid choice")
