# Configuration for Dead Reckoning System

# Hardware Configuration
MAGNETS_PER_REVOLUTION = 18  # 360/20 = 18 magnets
WHEEL_DIAMETER_M = 0.2  # Wheel diameter in meters (adjust to your vehicle)
WHEEL_CIRCUMFERENCE_M = WHEEL_DIAMETER_M * 3.14159265359

# Sensor Pins (adjust to your wiring)
HALL_SENSOR_PIN = 17  # GPIO pin for AS314 hall effect sensor
AS5600_I2C_ADDRESS = 0x36  # Default I2C address for AS5600

# Dead Reckoning Parameters
UPDATE_RATE_HZ = 100  # Target update rate in Hz
INITIAL_X = 0.0  # Starting X position (meters)
INITIAL_Y = 0.0  # Starting Y position (meters)
INITIAL_HEADING = 0.0  # Starting heading (radians)

# Data Logging
ENABLE_LOGGING = True
LOG_FILE = "path_log.csv"
LOG_INTERVAL = 10  # Log every N updates

# Web Dashboard
ENABLE_DASHBOARD = True
DASHBOARD_PORT = 5000
