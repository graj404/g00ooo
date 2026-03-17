import time
import numpy as np
try:
    import RPi.GPIO as GPIO
    import smbus2
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("Warning: RPi libraries not available. Running in simulation mode.")

import threading
from collections import deque
from config import HALL_SENSOR_PIN, AS5600_I2C_ADDRESS, MAGNETS_PER_REVOLUTION


class HallEffectSensor:
    """
    AS314 Hall Effect Sensor for RPM measurement
    Uses HARDWARE INTERRUPT for precise timing (not polling!)
    """
    
    def __init__(self, pin=HALL_SENSOR_PIN):
        self.pin = pin
        self.rpm = 0.0
        
        # Hardware interrupt timing (nanosecond precision)
        self.pulse_times = deque(maxlen=50)  # Store last 50 pulse timestamps
        self.lock = threading.Lock()
        
        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # ✅ HARDWARE INTERRUPT - captures pulse INSTANTLY
            GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,
                callback=self._pulse_interrupt,
                bouncetime=1  # 1ms debounce
            )
            print(f"Hall sensor using HARDWARE INTERRUPT on GPIO {self.pin} ✅")
        else:
            print("Hall sensor in simulation mode (no hardware)")
    
    def _pulse_interrupt(self, channel):
        """
        Hardware interrupt callback - fires INSTANTLY when pulse detected
        This runs in interrupt context - keep it FAST!
        """
        timestamp = time.perf_counter()  # Captured IMMEDIATELY ✅
        
        with self.lock:
            self.pulse_times.append(timestamp)
    
    def get_rpm(self):
        """
        Calculate RPM from hardware-captured pulse timestamps
        Uses actual time intervals between pulses (not assumed!)
        """
        with self.lock:
            if len(self.pulse_times) < 2:
                return 0.0
            
            # Get recent pulses
            pulses = list(self.pulse_times)
        
        # Calculate intervals between consecutive pulses
        intervals = [pulses[i+1] - pulses[i] for i in range(len(pulses)-1)]
        
        if not intervals:
            return 0.0
        
        # Average interval for stability
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval < 0.0001:  # Sanity check (< 0.1ms is impossible)
            return 0.0
        
        # RPM = (1 / interval) * (60 / magnets_per_rev)
        # This is EXACT timing from hardware ✅
        self.rpm = (1.0 / avg_interval) * (60.0 / MAGNETS_PER_REVOLUTION)
        
        return self.rpm
    
    def get_velocity_direct(self, wheel_circumference):
        """
        Calculate velocity directly from pulse intervals
        More accurate than RPM → velocity conversion
        """
        with self.lock:
            if len(self.pulse_times) < 2:
                return 0.0
            pulses = list(self.pulse_times)
        
        intervals = [pulses[i+1] - pulses[i] for i in range(len(pulses)-1)]
        
        if not intervals:
            return 0.0
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval < 0.0001:
            return 0.0
        
        # Distance per pulse = circumference / magnets
        distance_per_pulse = wheel_circumference / MAGNETS_PER_REVOLUTION
        
        # Velocity = distance / time (EXACT from hardware timing)
        velocity = distance_per_pulse / avg_interval
        
        return velocity
    
    def cleanup(self):
        if RPI_AVAILABLE:
            GPIO.cleanup(self.pin)


class AS5600Encoder:
    """AS5600 Magnetic Encoder for Steering Angle Sensor"""
    
    # AS5600 Register addresses
    REG_RAW_ANGLE_H = 0x0C
    REG_RAW_ANGLE_L = 0x0D
    REG_ANGLE_H = 0x0E
    REG_ANGLE_L = 0x0F
    
    def __init__(self, i2c_address=AS5600_I2C_ADDRESS, bus_number=1):
        self.address = i2c_address
        self.zero_offset = 0.0
        
        if RPI_AVAILABLE:
            self.bus = smbus2.SMBus(bus_number)
        else:
            self.bus = None
    
    def read_raw_angle(self):
        """Read raw angle from AS5600 (0-4095 for 0-360 degrees)"""
        if not RPI_AVAILABLE or self.bus is None:
            return 0
        
        try:
            high = self.bus.read_byte_data(self.address, self.REG_RAW_ANGLE_H)
            low = self.bus.read_byte_data(self.address, self.REG_RAW_ANGLE_L)
            raw_angle = (high << 8) | low
            return raw_angle
        except Exception as e:
            print(f"Error reading AS5600: {e}")
            return 0
    
    def get_angle_radians(self):
        """Get steering angle in radians"""
        raw = self.read_raw_angle()
        # Convert 12-bit value (0-4095) to radians (0-2π)
        angle_rad = (raw / 4096.0) * 2.0 * np.pi - self.zero_offset
        
        # Normalize to [-π, π]
        while angle_rad > np.pi:
            angle_rad -= 2.0 * np.pi
        while angle_rad < -np.pi:
            angle_rad += 2.0 * np.pi
        
        return angle_rad
    
    def calibrate_zero(self):
        """Set current position as zero reference"""
        raw = self.read_raw_angle()
        self.zero_offset = (raw / 4096.0) * 2.0 * np.pi
        print(f"AS5600 calibrated. Zero offset: {self.zero_offset:.4f} rad")
    
    def cleanup(self):
        if self.bus:
            self.bus.close()
