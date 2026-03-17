#!/usr/bin/env python3
"""
Dead Reckoning System for Vehicle Path Mapping
Raspberry Pi 5 8GB
Sensors: AS5600 (steering angle), AS314 (hall effect for RPM)
"""

import time
import numpy as np
import signal
import sys
import threading
from sensors import HallEffectSensor, AS5600Encoder
from lap_counter import LapCounter
from web_dashboard import start_dashboard, update_vehicle_state
from config import (
    WHEEL_CIRCUMFERENCE_M, UPDATE_RATE_HZ,
    INITIAL_X, INITIAL_Y, INITIAL_HEADING,
    ENABLE_LOGGING, LOG_FILE, LOG_INTERVAL,
    ENABLE_DASHBOARD, DASHBOARD_PORT
)


class DeadReckoningSystem:
    """Dead reckoning navigation using steering angle and wheel speed"""
    
    def __init__(self):
        # Initialize sensors
        self.hall_sensor = HallEffectSensor()
        self.steering_encoder = AS5600Encoder()
        
        # State variables (using numpy for fast computation)
        self.position = np.array([INITIAL_X, INITIAL_Y], dtype=np.float64)
        self.heading = INITIAL_HEADING  # radians
        self.velocity = 0.0  # m/s
        self.rpm = 0.0
        self.steering_angle = 0.0
        
        # Lap counter
        self.lap_counter = LapCounter(start_threshold=2.0, min_lap_distance=10.0)
        
        # Timing
        self.dt = 1.0 / UPDATE_RATE_HZ
        self.last_update = time.perf_counter()
        
        # Logging
        self.update_count = 0
        if ENABLE_LOGGING:
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize CSV log file"""
        with open(LOG_FILE, 'w') as f:
            f.write("timestamp,x,y,heading,velocity,steering_angle,rpm,laps,lap_distance\n")
    
    def update(self):
        """Main update loop - calculate new position using dead reckoning"""
        current_time = time.perf_counter()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Read sensors
        self.rpm = self.hall_sensor.get_rpm()
        self.steering_angle = self.steering_encoder.get_angle_radians()
        
        # Calculate velocity from RPM
        # velocity = (RPM / 60) * wheel_circumference
        self.velocity = (self.rpm / 60.0) * WHEEL_CIRCUMFERENCE_M
        
        # Dead reckoning calculation using numpy
        # For small steering angles, approximate as straight line
        # For larger angles, use circular arc model
        
        if abs(self.steering_angle) < 0.01:  # Nearly straight
            # Simple linear motion
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            # Circular arc motion (Ackermann steering approximation)
            # Simplified: heading rate proportional to steering angle
            heading_rate = self.velocity * np.tan(self.steering_angle) / 1.0  # Assuming 1m wheelbase
            
            # Update heading
            self.heading += heading_rate * dt
            
            # Normalize heading to [-π, π]
            self.heading = np.arctan2(np.sin(self.heading), np.cos(self.heading))
            
            # Update position
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        
        # Update lap counter
        laps, lap_dist, total_dist, lap_completed = self.lap_counter.update(self.position)
        
        # Update web dashboard
        if ENABLE_DASHBOARD:
            update_vehicle_state(
                self.position[0], self.position[1], self.heading, self.velocity,
                self.rpm, self.steering_angle, laps, lap_dist, total_dist
            )
        
        # Logging
        self.update_count += 1
        if ENABLE_LOGGING and self.update_count % LOG_INTERVAL == 0:
            self._log_data(current_time, laps, lap_dist)
        
        return self.position, self.heading, self.velocity, laps
    
    def _log_data(self, timestamp, laps, lap_distance):
        """Log current state to file"""
        with open(LOG_FILE, 'a') as f:
            f.write(f"{timestamp:.3f},{self.position[0]:.4f},{self.position[1]:.4f},"
                   f"{self.heading:.4f},{self.velocity:.4f},{self.steering_angle:.4f},"
                   f"{self.rpm:.2f},{laps},{lap_distance:.2f}\n")
    
    def get_position(self):
        """Get current position as (x, y) tuple"""
        return tuple(self.position)
    
    def get_heading_degrees(self):
        """Get heading in degrees"""
        return np.degrees(self.heading)
    
    def reset_position(self, x=0.0, y=0.0, heading=0.0):
        """Reset position and heading"""
        self.position = np.array([x, y], dtype=np.float64)
        self.heading = heading
        print(f"Position reset to: ({x:.2f}, {y:.2f}), heading: {np.degrees(heading):.1f}°")
    
    def calibrate_sensors(self):
        """Calibrate sensors (call when vehicle is straight)"""
        print("Calibrating sensors...")
        self.steering_encoder.calibrate_zero()
        print("Calibration complete.")
    
    def cleanup(self):
        """Clean up resources"""
        self.hall_sensor.cleanup()
        self.steering_encoder.cleanup()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    if 'dr_system' in globals():
        dr_system.cleanup()
    sys.exit(0)


def main():
    global dr_system
    
    print("=" * 50)
    print("Dead Reckoning System - Vehicle Path Mapping")
    print("=" * 50)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start web dashboard in background thread
    if ENABLE_DASHBOARD:
        dashboard_thread = threading.Thread(
            target=start_dashboard, 
            kwargs={'host': '0.0.0.0', 'port': DASHBOARD_PORT},
            daemon=True
        )
        dashboard_thread.start()
        time.sleep(2)  # Give dashboard time to start
    
    # Initialize system
    dr_system = DeadReckoningSystem()
    
    # Calibrate sensors
    input("Position vehicle straight ahead, then press Enter to calibrate...")
    dr_system.calibrate_sensors()
    
    print(f"\nStarting dead reckoning at {UPDATE_RATE_HZ} Hz")
    if ENABLE_DASHBOARD:
        print(f"Dashboard: http://localhost:{DASHBOARD_PORT}")
    print("Press Ctrl+C to stop\n")
    
    # Main loop
    loop_count = 0
    try:
        while True:
            # Update dead reckoning
            position, heading, velocity, laps = dr_system.update()
            
            # Display status every second
            loop_count += 1
            if loop_count % UPDATE_RATE_HZ == 0:
                x, y = position
                heading_deg = np.degrees(heading)
                lap_info = dr_system.lap_counter.get_lap_info()
                print(f"Pos: ({x:7.2f}, {y:7.2f}) m | "
                      f"Heading: {heading_deg:6.1f}° | "
                      f"Velocity: {velocity:5.2f} m/s | "
                      f"Laps: {laps}")
            
            # Sleep to maintain update rate
            time.sleep(dr_system.dt)
    
    except KeyboardInterrupt:
        pass
    finally:
        dr_system.cleanup()
        print(f"\nPath data saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()
