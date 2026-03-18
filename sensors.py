import time
import numpy as np
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from gpiozero import DigitalInputDevice
    import smbus2
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("Warning: RPi libraries not available. Running in simulation mode.")

import threading
from collections import deque
from config import IR_SENSOR_PIN, AS5600_I2C_ADDRESS, MAGNETS_PER_REVOLUTION, FUEL_ADC_CHANNEL, MIN_FUEL_VOLTAGE, MAX_FUEL_VOLTAGE


class IRSensor:
    """
    IR Sensor for RPM measurement using gpiozero
    Counts pulses to calculate RPS/RPM
    """
    
    def __init__(self, pin=IR_SENSOR_PIN):
        self.pin = pin
        self.rpm = 0.0
        self.rps = 0.0
        self.count = 0
        self.last_state = 0
        
        # Timing for RPS calculation
        self.pulse_times = deque(maxlen=50)
        self.lock = threading.Lock()
        
        if RPI_AVAILABLE:
            # Use gpiozero for IR sensor
            self.sensor = DigitalInputDevice(self.pin, pull_up=False)
            
            # Start counting thread
            self.running = True
            self.counter_thread = threading.Thread(target=self._count_pulses, daemon=True)
            self.counter_thread.start()
        else:
            print("IR sensor in simulation mode (no hardware)")
            self.sensor = None
    
    def _count_pulses(self):
        """
        Count pulses from IR sensor and calculate RPS
        """
        start_time = time.time()
        
        while self.running:
            if self.sensor:
                current_state = self.sensor.value
                
                # Detect rising edge
                if current_state == 1 and self.last_state == 0:
                    timestamp = time.perf_counter()
                    with self.lock:
                        self.count += 1
                        self.pulse_times.append(timestamp)
                
                self.last_state = current_state
            
            # Calculate RPS every second
            if time.time() - start_time >= 1.0:
                with self.lock:
                    self.rps = self.count
                    self.rpm = self.rps * 60.0
                    self.count = 0
                start_time = time.time()
            
            time.sleep(0.001)  # 1ms polling
    
    def get_rpm(self):
        """
        Calculate RPM from pulse timestamps
        """
        with self.lock:
            return self.rpm
    
    def get_rps(self):
        """Get revolutions per second"""
        with self.lock:
            return self.rps
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.sensor:
            self.sensor.close()
        
        # RPM = (1 / interval) * (60 / magnets_per_rev)
        # This is EXACT timing from hardware ✅
        self.rpm = (1.0 / avg_interval) * (60.0 / MAGNETS_PER_REVOLUTION)
        
    def get_rpm(self):
        """
        Calculate RPM from pulse timestamps
        """
        with self.lock:
            return self.rpm
    
    def get_rps(self):
        """Get revolutions per second"""
        with self.lock:
            return self.rps
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.sensor:
            self.sensor.close()


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
    
    def cleanup(self):
        if self.bus:
            self.bus.close()



class FuelSensor:
    """
    Fuel level sensor using ADS1115 ADC
    Reads analog voltage and converts to fuel percentage
    """
    
    def __init__(self, channel=FUEL_ADC_CHANNEL, min_voltage=MIN_FUEL_VOLTAGE, max_voltage=MAX_FUEL_VOLTAGE):
        self.channel = channel
        self.min_voltage = min_voltage
        self.max_voltage = max_voltage
        self.fuel_level = 100.0
        
        if RPI_AVAILABLE:
            try:
                # Initialize I2C and ADS1115
                i2c = busio.I2C(board.SCL, board.SDA)
                ads = ADS.ADS1115(i2c)
                
                # Create analog input channel
                if channel == 0:
                    self.chan = AnalogIn(ads, ADS.P0)
                elif channel == 1:
                    self.chan = AnalogIn(ads, ADS.P1)
                elif channel == 2:
                    self.chan = AnalogIn(ads, ADS.P2)
                elif channel == 3:
                    self.chan = AnalogIn(ads, ADS.P3)
                else:
                    raise ValueError(f"Invalid ADC channel: {channel}")
                
                print(f"Fuel sensor initialized on ADC channel {channel}")
            except Exception as e:
                print(f"Error initializing fuel sensor: {e}")
                self.chan = None
        else:
            print("Fuel sensor in simulation mode (no hardware)")
            self.chan = None
    
    def read_fuel_level(self):
        """
        Read fuel level from ADC and convert to percentage
        Returns: fuel level as percentage (0-100)
        """
        if not self.chan:
            return 100.0  # Default value in simulation mode
        
        try:
            # Read voltage from ADC
            voltage = self.chan.voltage
            
            # Convert voltage to fuel percentage
            # Assuming voltage decreases as fuel decreases
            fuel = ((voltage - self.min_voltage) / (self.max_voltage - self.min_voltage)) * 100.0
            
            # Invert if needed (100% = full tank)
            fuel = 100.0 - fuel
            
            # Clamp to 0-100 range
            fuel = max(0.0, min(100.0, fuel))
            
            self.fuel_level = fuel
            return fuel
        
        except Exception as e:
            print(f"Error reading fuel sensor: {e}")
            return self.fuel_level  # Return last known value
    
    def get_voltage(self):
        """Get raw voltage reading"""
        if not self.chan:
            return 0.0
        
        try:
            return self.chan.voltage
        except Exception as e:
            print(f"Error reading voltage: {e}")
            return 0.0
