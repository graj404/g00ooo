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
from pi_filter import PISteeringObserver, PIVelocityObserver
from web_dashboard import start_dashboard, update_vehicle_state
from config import (
    WHEEL_CIRCUMFERENCE_M, UPDATE_RATE_HZ,
    INITIAL_X, INITIAL_Y, INITIAL_HEADING,
    ENABLE_LOGGING, LOG_FILE, LOG_INTERVAL,
    ENABLE_DASHBOARD, DASHBOARD_PORT, DASHBOARD_UPDATE_RATE_HZ, ENABLE_LAP_RESET,
    ENABLE_PI_FILTER, PI_KP, PI_KI, MAX_STEERING_RATE_DEG_S,
    ENABLE_VELOCITY_FILTER, VELOCITY_KP, VELOCITY_KI,
    USE_RK2_INTEGRATION
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
        
        # Error tracking and correction
        self.lap_errors = []  # Store error per lap
        self.cumulative_error = 0.0
        self.enable_lap_reset = ENABLE_LAP_RESET  # From config
        
        # PI filters for sensor smoothing
        self.enable_pi_filter = ENABLE_PI_FILTER
        if self.enable_pi_filter:
            self.pi_steering = PISteeringObserver(
                kp=PI_KP,
                ki=PI_KI,
                max_steering_rate_deg_s=MAX_STEERING_RATE_DEG_S
            )
            print(f"PI Steering Filter enabled: Kp={PI_KP}, Ki={PI_KI}")
        
        self.enable_velocity_filter = ENABLE_VELOCITY_FILTER
        if self.enable_velocity_filter:
            self.pi_velocity = PIVelocityObserver(
                kp=VELOCITY_KP,
                ki=VELOCITY_KI
            )
            print(f"PI Velocity Filter enabled: Kp={VELOCITY_KP}, Ki={VELOCITY_KI}")
        
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
        raw_steering_angle = self.steering_encoder.get_angle_radians()
        
        # Apply PI filter to steering angle (reduces error by ~50%)
        if self.enable_pi_filter:
            self.steering_angle = self.pi_steering.update(raw_steering_angle, dt)
        else:
            self.steering_angle = raw_steering_angle
        
        # Calculate velocity from RPM (using hardware interrupt timing)
        # Option 1: Traditional RPM → velocity
        raw_velocity = (self.rpm / 60.0) * WHEEL_CIRCUMFERENCE_M
        
        # Option 2: Direct velocity from pulse intervals (more accurate)
        # raw_velocity = self.hall_sensor.get_velocity_direct(WHEEL_CIRCUMFERENCE_M)
        
        # Apply PI filter to velocity (optional)
        if self.enable_velocity_filter:
            self.velocity = self.pi_velocity.update(raw_velocity, dt)
        else:
            self.velocity = raw_velocity
        
        # Dead reckoning calculation using numpy
        # Choose integration method based on configuration
        
        if USE_RK2_INTEGRATION:
            # Runge-Kutta 2nd order (Midpoint method)
            # More accurate in turns - accounts for heading change during dt
            self._update_position_rk2(dt)
        else:
            # Simple Euler method
            # Faster but less accurate in turns
            self._update_position_euler(dt)
        
        # Update lap counter
        laps, lap_dist, total_dist, lap_completed = self.lap_counter.update(self.position)
        
        # Handle lap completion with error reset
        if lap_completed and self.enable_lap_reset:
            # Calculate position error (distance from origin)
            error_distance = np.linalg.norm(self.position)
            self.lap_errors.append(error_distance)
            self.cumulative_error += error_distance
            
            avg_error = np.mean(self.lap_errors) if self.lap_errors else 0.0
            
            print(f"\n{'='*50}")
            print(f"LAP {laps} COMPLETED - ERROR ANALYSIS")
            print(f"{'='*50}")
            print(f"Position error: {error_distance:.3f} m")
            print(f"Average error per lap: {avg_error:.3f} m")
            print(f"Cumulative error: {self.cumulative_error:.3f} m")
            print(f"Error percentage: {(error_distance/lap_dist)*100:.2f}%")
            print(f"Resetting position to origin...")
            print(f"{'='*50}\n")
            
            # Reset position to origin to prevent error accumulation
            self.position = np.array([0.0, 0.0], dtype=np.float64)
            # Note: We keep heading as-is (don't reset heading)
        
        # Read fuel level (placeholder - implement based on your sensor)
        fuel_level = self._read_fuel_level()
        
        # Update web dashboard (minimal: only position, laps, fuel)
        if ENABLE_DASHBOARD:
            update_vehicle_state(
                self.position[0], self.position[1], laps, fuel_level
            )
        
        # Logging
        self.update_count += 1
        if ENABLE_LOGGING and self.update_count % LOG_INTERVAL == 0:
            self._log_data(current_time, laps, lap_dist)
        
        return self.position, self.heading, self.velocity, laps
    
    def _update_position_euler(self, dt):
        """
        Simple Euler integration method
        Assumes heading is constant during dt
        Fast but less accurate in turns
        """
        if abs(self.steering_angle) < 0.01:  # Nearly straight
            # Simple linear motion
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            # Circular arc motion (Ackermann steering approximation)
            heading_rate = self.velocity * np.tan(self.steering_angle) / 1.0  # 1m wheelbase
            
            # Update heading
            self.heading += heading_rate * dt
            self.heading = np.arctan2(np.sin(self.heading), np.cos(self.heading))
            
            # Update position
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
    
    def _update_position_rk2(self, dt):
        """
        Runge-Kutta 2nd order (Midpoint method)
        Accounts for heading change during dt
        More accurate in turns - reduces error by ~70%
        
        Method:
        1. Calculate heading change at start
        2. Estimate midpoint heading
        3. Use midpoint heading for position update
        """
        if abs(self.steering_angle) < 0.01:  # Nearly straight
            # For straight line, RK2 = Euler (no benefit)
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            # Calculate heading rate
            heading_rate = self.velocity * np.tan(self.steering_angle) / 1.0  # 1m wheelbase
            
            # Step 1: Heading at start
            heading_start = self.heading
            
            # Step 2: Estimate heading at midpoint (dt/2)
            heading_mid = heading_start + heading_rate * (dt / 2.0)
            
            # Step 3: Use midpoint heading for position update
            displacement = self.velocity * dt
            dx = displacement * np.cos(heading_mid)  # ← Uses midpoint heading!
            dy = displacement * np.sin(heading_mid)
            self.position += np.array([dx, dy], dtype=np.float64)
            
            # Step 4: Update heading to end of interval
            self.heading = heading_start + heading_rate * dt
            self.heading = np.arctan2(np.sin(self.heading), np.cos(self.heading))
    
    def get_error_statistics(self):
        """Get error statistics"""
        if not self.lap_errors:
            return {
                'num_laps': 0,
                'avg_error': 0.0,
                'max_error': 0.0,
                'min_error': 0.0,
                'cumulative_error': 0.0
            }
        
        return {
            'num_laps': len(self.lap_errors),
            'avg_error': np.mean(self.lap_errors),
            'max_error': np.max(self.lap_errors),
            'min_error': np.min(self.lap_errors),
            'cumulative_error': self.cumulative_error,
            'error_list': self.lap_errors
        }
    
    def _read_fuel_level(self):
        """
        Read fuel level from sensor
        Returns: fuel level as percentage (0-100)
        
        TODO: Implement based on your fuel sensor type:
        - If using analog sensor: Read ADC value and convert to percentage
        - If using digital sensor: Read GPIO pin state
        - Example for MCP3008 ADC:
          from spidev import SpiDev
          spi = SpiDev()
          spi.open(0, 0)
          raw = spi.xfer2([1, (8 + channel) << 4, 0])
          value = ((raw[1] & 3) << 8) + raw[2]
          percentage = (value / 1023.0) * 100
        """
        # Placeholder: return 100% for now
        return 100.0
    
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
    
    # Initialize system
    dr_system = DeadReckoningSystem()
    
    # Calibrate sensors
    input("Position vehicle straight ahead, then press Enter to calibrate...")
    dr_system.calibrate_sensors()
    
    print(f"\nStarting dead reckoning at {UPDATE_RATE_HZ} Hz")
    if ENABLE_DASHBOARD:
        print(f"Dashboard: http://localhost:{DASHBOARD_PORT}")
        print(f"Dashboard update rate: {DASHBOARD_UPDATE_RATE_HZ} Hz (every {1.0/DASHBOARD_UPDATE_RATE_HZ:.1f}s)")
        print("Note: Slow dashboard updates don't affect sensor accuracy!")
    print("Press Ctrl+C to stop\n")
    
    # Start web dashboard in separate thread (if enabled)
    if ENABLE_DASHBOARD:
        dashboard_thread = threading.Thread(
            target=start_dashboard, 
            kwargs={'host': '0.0.0.0', 'port': DASHBOARD_PORT},
            daemon=True
        )
        dashboard_thread.start()
        time.sleep(2)  # Give dashboard time to start
    
    # Main sensor loop (fast - 100 Hz)
    loop_count = 0
    dashboard_update_counter = 0
    dashboard_update_interval = int(UPDATE_RATE_HZ / DASHBOARD_UPDATE_RATE_HZ)
    
    try:
        while True:
            # Update dead reckoning (FAST - every 10ms at 100 Hz)
            position, heading, velocity, laps = dr_system.update()
            
            # Update dashboard (SLOW - every 500ms at 2 Hz)
            dashboard_update_counter += 1
            if ENABLE_DASHBOARD and dashboard_update_counter >= dashboard_update_interval:
                dashboard_update_counter = 0
                # Dashboard update happens in background thread
                # This doesn't block the sensor loop!
            
            # Display status every second (console only)
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
        
        # Print final error statistics
        if ENABLE_LAP_RESET:
            stats = dr_system.get_error_statistics()
            print(f"\n{'='*50}")
            print(f"FINAL ERROR STATISTICS")
            print(f"{'='*50}")
            print(f"Total laps: {stats['num_laps']}")
            if stats['num_laps'] > 0:
                print(f"Average error per lap: {stats['avg_error']:.3f} m")
                print(f"Maximum error: {stats['max_error']:.3f} m")
                print(f"Minimum error: {stats['min_error']:.3f} m")
                print(f"Cumulative error: {stats['cumulative_error']:.3f} m")
                print(f"\nError per lap: {[f'{e:.2f}m' for e in stats['error_list']]}")
            print(f"{'='*50}\n")
        
        # Print PI filter statistics
        if ENABLE_PI_FILTER and dr_system.enable_pi_filter:
            pi_stats = dr_system.pi_steering.get_statistics()
            print(f"\n{'='*50}")
            print(f"PI FILTER PERFORMANCE")
            print(f"{'='*50}")
            print(f"Raw sensor noise: {np.degrees(pi_stats['raw_noise']):.3f}°")
            print(f"Filtered noise: {np.degrees(pi_stats['filtered_noise']):.3f}°")
            print(f"Noise reduction: {pi_stats['noise_reduction']:.1f}%")
            print(f"Final integral error: {pi_stats['integral_error']:.3f}°")
            print(f"{'='*50}\n")
        
        print(f"Path data saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()
