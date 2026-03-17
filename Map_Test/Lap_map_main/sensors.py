import time
import numpy as np
try:
    import RPi.GPIO as GPIO
    import smbus2
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("Warning: RPi libraries not available. Running in simulation mode.")

from config import HALL_SENSOR_PIN, AS5600_I2C_ADDRESS, MAGNETS_PER_REVOLUTION


class HallEffectSensor:
    """AS314 Hall Effect Sensor for RPM measurement"""
    
    def __init__(self, pin=HALL_SENSOR_PIN):
        self.pin = pin
        self.pulse_count = 0
        self.last_time = time.perf_counter()
        self.rpm = 0.0
        
        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self._pulse_callback)
    
    def _pulse_callback(self, channel):
        self.pulse_count += 1
    
    def get_rpm(self):
        """Calculate RPM based on pulse count"""
        current_time = time.perf_counter()
        dt = current_time - self.last_time
        
        if dt >= 0.1:  # Update every 100ms minimum
            pulses = self.pulse_count
            self.pulse_count = 0
            self.last_time = current_time
            
            # RPM = (pulses / magnets_per_rev) * (60 / dt)
            self.rpm = (pulses / MAGNETS_PER_REVOLUTION) * (60.0 / dt)
        
        return self.rpm
    
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
