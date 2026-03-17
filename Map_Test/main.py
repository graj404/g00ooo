#!/usr/bin/env python3
"""
Dead Reckoning System - TESTING VERSION
Manual input for SAS and velocity sensors
"""

import time
import numpy as np
import signal
import sys
import threading
from lap_counter import LapCounter
from web_dashboard import start_dashboard, update_vehicle_state
from config import (
    UPDATE_RATE_HZ,
    INITIAL_X, INITIAL_Y, INITIAL_HEADING,
    ENABLE_LOGGING, LOG_FILE, LOG_INTERVAL,
    ENABLE_DASHBOARD, DASHBOARD_PORT
)


class DeadReckoningSystemTest:
    """Dead reckoning navigation with manual sensor input for testing"""
    
    def __init__(self):
        # State variables (using numpy for fast computation)
        self.position = np.array([INITIAL_X, INITIAL_Y], dtype=np.float64)
        self.heading = INITIAL_HEADING  # radians
        self.velocity = 0.0  # m/s (manual input)
        self.steering_angle = 0.0  # radians (manual input)
        self.fuel_level = 100.0  # percentage
        
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
            f.write("timestamp,x,y,heading,velocity,steering_angle,dt,laps,lap_distance,fuel_level\n")
    
    def set_manual_input(self, steering_angle_rad, velocity_ms, fuel_percent=None):
        """Set manual sensor values for testing"""
        self.steering_angle = steering_angle_rad
        self.velocity = velocity_ms
        if fuel_percent is not None:
            self.fuel_level = fuel_percent
    
    def update(self):
        """
        Main update loop - calculate new position using dead reckoning
        
        FORMULAS USED:
        1. Linear Motion (straight line, |steering_angle| < 0.01 rad):
           displacement = velocity * dt
           dx = displacement * cos(heading)
           dy = displacement * sin(heading)
           position = position + [dx, dy]
        
        2. Circular Arc Motion (turning, |steering_angle| >= 0.01 rad):
           heading_rate = (velocity * tan(steering_angle)) / wheelbase
           heading = heading + heading_rate * dt
           heading = atan2(sin(heading), cos(heading))  # Normalize to [-π, π]
           displacement = velocity * dt
           dx = displacement * cos(heading)
           dy = displacement * sin(heading)
           position = position + [dx, dy]
        
        3. Velocity from RPM (hardware only):
           velocity = (RPM / 60) * wheel_circumference
        
        4. Distance calculation:
           distance = ||current_position - last_position||  # Euclidean norm
        """
        current_time = time.perf_counter()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Dead reckoning calculation using numpy
        if abs(self.steering_angle) < 0.01:  # Nearly straight
            # Formula: Linear motion
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            # Formula: Circular arc motion (Ackermann steering)
            wheelbase = 1.0  # meters (adjust to your vehicle)
            heading_rate = self.velocity * np.tan(self.steering_angle) / wheelbase
            
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
                0.0,  # RPM not used in test
                self.steering_angle, laps, lap_dist, total_dist, dt, self.fuel_level
            )
        
        # Logging
        self.update_count += 1
        if ENABLE_LOGGING and self.update_count % LOG_INTERVAL == 0:
            self._log_data(current_time, laps, lap_dist, dt)
        
        return self.position, self.heading, self.velocity, laps
    
    def _log_data(self, timestamp, laps, lap_distance, dt):
        """Log current state to file"""
        with open(LOG_FILE, 'a') as f:
            f.write(f"{timestamp:.3f},{self.position[0]:.4f},{self.position[1]:.4f},"
                   f"{self.heading:.4f},{self.velocity:.4f},{self.steering_angle:.4f},"
                   f"{dt:.4f},{laps},{lap_distance:.2f},{self.fuel_level:.1f}\n")
    
    def reset_position(self, x=0.0, y=0.0, heading=0.0):
        """Reset position and heading"""
        self.position = np.array([x, y], dtype=np.float64)
        self.heading = heading
        self.lap_counter.reset()
        print(f"Position reset to: ({x:.2f}, {y:.2f}), heading: {np.degrees(heading):.1f}°")


# Global instance for API access
dr_system = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down...")
    sys.exit(0)


def main():
    global dr_system
    
    print("=" * 50)
    print("Dead Reckoning System - TESTING MODE")
    print("=" * 50)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start web dashboard in background thread
    if ENABLE_DASHBOARD:
        dashboard_thread = threading.Thread(
            target=start_dashboard, 
            kwargs={'host': '0.0.0.0', 'port': DASHBOARD_PORT, 'test_system': None},
            daemon=True
        )
        dashboard_thread.start()
        time.sleep(2)  # Give dashboard time to start
    
    # Initialize system
    dr_system = DeadReckoningSystemTest()
    
    print(f"\nStarting dead reckoning at {UPDATE_RATE_HZ} Hz")
    print(f"Dashboard: http://localhost:{DASHBOARD_PORT}")
    print("Use the web interface to input steering angle and velocity\n")
    
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
                print(f"Pos: ({x:7.2f}, {y:7.2f}) m | "
                      f"Heading: {heading_deg:6.1f}° | "
                      f"Velocity: {velocity:5.2f} m/s | "
                      f"Laps: {laps}")
            
            # Sleep to maintain update rate
            time.sleep(dr_system.dt)
    
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\nPath data saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()
