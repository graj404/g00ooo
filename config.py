# Configuration for Dead Reckoning System

# Hardware Configuration
MAGNETS_PER_REVOLUTION = 1  # Number of pulses per wheel revolution (1 for single reflector/IR sensor)
WHEEL_DIAMETER_M = 0.275  # Wheel diameter in meters (27.5cm from your code)
WHEEL_CIRCUMFERENCE_M = WHEEL_DIAMETER_M * 3.14159265359
WHEEL_BASE_M = 1.2  # Distance between front and rear axles in meters

# Sensor Pins (adjust to your wiring)
IR_SENSOR_PIN = 27  # GPIO pin for IR sensor
AS5600_I2C_ADDRESS = 0x36  # Default I2C address for AS5600

# Fuel Sensor Configuration (ADS1115 ADC)
FUEL_ADC_CHANNEL = 0  # ADC channel (0-3) for fuel sensor
MIN_FUEL_VOLTAGE = 0.04  # Voltage at empty tank
MAX_FUEL_VOLTAGE = 0.7   # Voltage at full tank

# Dead Reckoning Parameters
# Update rate: How many times per second we calculate position
# Higher = more accurate but more CPU usage
# 
# Recommended values:
#   100 Hz (0.01s) - Good for go-kart (20-30cm accuracy at racing speed)
#   200 Hz (0.005s) - Better accuracy (10-15cm at racing speed)
#   1000 Hz (0.001s) - Overkill for go-kart (2-3cm accuracy, high CPU)
#
# At 100 Hz and 20 m/s (72 km/h):
#   - Distance per update: 0.2m (20cm)
#   - Total updates per second: 100
#   - CPU usage: ~5%
#
# At 1000 Hz and 20 m/s:
#   - Distance per update: 0.02m (2cm)
#   - Total updates per second: 1000
#   - CPU usage: ~30%
UPDATE_RATE_HZ = 100  # Target update rate in Hz (100 = every 10ms)

# Integration Method
USE_RK2_INTEGRATION = True  # Use Runge-Kutta 2nd order (more accurate in turns)
# When True: Uses midpoint method, reduces turn error by ~70%
# When False: Uses simple Euler method (faster but less accurate)

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
DASHBOARD_UPDATE_RATE_HZ = 2  # Update display at 2 Hz (every 500ms)
# Slow dashboard updates don't affect sensor accuracy!
# Sensor loop runs at 100 Hz, display at 2 Hz

# Error Management
ENABLE_LAP_RESET = True  # Reset position at each lap to prevent error accumulation
# When True: Position resets to (0,0) after each lap
# When False: Error accumulates over multiple laps (can reach 50m+ after 50 laps)

# PI Filter Configuration (Reduces error by ~50%)
ENABLE_PI_FILTER = True  # Use PI observer for steering angle
PI_KP = 0.8  # Proportional gain (0.6-1.0 recommended)
PI_KI = 0.05  # Integral gain (0.03-0.1 recommended)
MAX_STEERING_RATE_DEG_S = 120.0  # Physical steering rate limit (degrees/second)

# Optional: PI filter for velocity (less critical than steering)
ENABLE_VELOCITY_FILTER = False
VELOCITY_KP = 0.7
VELOCITY_KI = 0.03
