# Configuration for Dead Reckoning System - TESTING VERSION

# Dead Reckoning Parameters - TESTING VERSION
# Update rate: How many times per second we calculate position
# 
# For testing, 100 Hz is perfect:
#   - Fast enough to see smooth motion
#   - Slow enough to observe individual updates
#   - Matches hardware version
UPDATE_RATE_HZ = 100  # Target update rate in Hz (100 = every 10ms)

INITIAL_X = 0.0  # Starting X position (meters)
INITIAL_Y = 0.0  # Starting Y position (meters)
INITIAL_HEADING = 0.0  # Starting heading (radians)

# Data Logging
ENABLE_LOGGING = True
LOG_FILE = "path_log_test.csv"
LOG_INTERVAL = 10  # Log every N updates

# Web Dashboard
ENABLE_DASHBOARD = True
DASHBOARD_PORT = 5001  # Different port from hardware version
