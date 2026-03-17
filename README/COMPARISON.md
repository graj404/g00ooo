# Hardware vs Testing Comparison

## Side-by-Side Comparison

| Aspect | Lap_map_main (Hardware) | Map_Test (Testing) |
|--------|------------------------|-------------------|
| **Purpose** | Production deployment on Raspberry Pi | Development and testing |
| **Display** | 5" screen (800x480) | Full screen browser |
| **Port** | 5000 | 5001 |
| **Sensors** | AS5600 (I2C) + AS314 (GPIO) | Manual web input |
| **Dashboard** | Minimal (map + laps + fuel) | Detailed (all metrics) |
| **Lap Counter** | Top right, large font | Top right, large font |
| **Position** | Pulsing circle on map | Pulsing circle on map |
| **Fuel Display** | Bottom right with color bar | Manual slider + display |
| **Update Rate** | 100 Hz | 100 Hz |
| **Dashboard Update** | 10 Hz | 10 Hz |
| **Dependencies** | RPi.GPIO, smbus2, FastAPI | FastAPI only |

## Dashboard Layouts

### Hardware Dashboard (Lap_map_main)

**Optimized for 5" display while driving**

```
┌─────────────────────────────────────────┐
│                                  ┌────┐ │
│                                  │LAP │ │
│                                  │ 3  │ │ ← Large, easy to read
│                                  └────┘ │
│                                         │
│                                         │
│         [Vehicle Path Map]              │
│                                         │
│              ●  ← Current Position      │
│             (pulsing green circle)      │
│                                         │
│                                         │
│                                         │
│                                  ┌────┐ │
│                                  │FUEL│ │
│                                  │▓▓▓▓│ │ ← Color coded
│                                  │75% │ │   (green/yellow/red)
│                                  └────┘ │
└─────────────────────────────────────────┘
     800 x 480 pixels (5" display)
```

**Features:**
- Clean, distraction-free
-  Large lap counter (48px font)
-  Pulsing position indicator
-  Auto-scaling map
-  Fuel bar with color coding
-  No sensor details (not needed while driving)
-  No calculation steps (not needed while driving)

### Testing Dashboard (Map_Test)

**Detailed for development and debugging**

```
┌─────────────────────────────────────────────────────────┐
│     VEHICLE TESTING DASHBOARD                           │
├─────────────────────────────────────────────────────────┤
│  MANUAL INPUT CONTROLS                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│  │ Steering: 0° │ │ Velocity: 0  │ │ Fuel: 100%   │     │
│  └──────────────┘ └──────────────┘ └──────────────┘     │
│  [UPDATE SENSORS] [RESET POSITION]                      │
├──────────────────────┬──────────────────────────────────┤
│ SENSOR INPUTS        │                           ┌────┐ │
│ • SAS: 0.0°          │                           │LAP │ │
│ • Velocity: 0.00 m/s │                           │ 0  │ │
│ • RPM: 0 rpm         │                           └────┘ │
│ • Fuel: 100%         │                                  │
│                      │                                  │
│ CALCULATIONS         │    [Vehicle Path Map]            │
│ • Δt: 0.010 s        │                                  │
│ • Heading: 0.0°      │         ●  ← Position            │
│ • Distance: 0.000 m  │        (pulsing circle)          │
│                      │                                  │
│ POSITION & DISTANCE  │                                  │
│ • X: 0.00 m          │                                  │
│ • Y: 0.00 m          │                                  │
│ • Current Lap: 0.0 m │                                  │
│ • Total: 0.0 m       │                                  │
└──────────────────────┴──────────────────────────────────┘
           Full screen browser window
```

**Features:**
- ✅ Manual input controls
- ✅ All sensor readings visible
- ✅ Calculation steps shown
- ✅ Detailed position metrics
- ✅ Same lap counting logic
- ✅ Real-time formula verification
- ✅ Testing without hardware

## Code Differences

### main.py Comparison

#### Hardware (Lap_map_main/main.py)
```python
# Read from hardware sensors
self.rpm = self.hall_sensor.get_rpm()
self.steering_angle = self.steering_encoder.get_angle_radians()
self.velocity = (self.rpm / 60.0) * WHEEL_CIRCUMFERENCE_M

# Update minimal dashboard
update_vehicle_state(
    self.position[0], self.position[1], 
    laps, fuel_level
)
```

#### Testing (Map_Test/main.py)
```python
# Use manual input values
# self.steering_angle and self.velocity set via web API

# Update detailed dashboard
update_vehicle_state(
    self.position[0], self.position[1], 
    self.heading, self.velocity,
    0.0, self.steering_angle, 
    laps, lap_dist, total_dist, 
    dt, self.fuel_level
)
```

### web_dashboard.py Comparison

#### Hardware (Lap_map_main/web_dashboard.py)
```python
# Minimal state
vehicle_state = {
    'x': 0.0,
    'y': 0.0,
    'laps_completed': 0,
    'fuel_level': 100.0,
    'path_points': []
}

# Simple update function
def update_vehicle_state(x, y, laps, fuel_level=None):
    # Only essential data
```

#### Testing (Map_Test/web_dashboard.py)
```python
# Detailed state
vehicle_state = {
    'x': 0.0,
    'y': 0.0,
    'heading': 0.0,
    'velocity': 0.0,
    'rpm': 0.0,
    'steering_angle': 0.0,
    'laps_completed': 0,
    'current_lap_distance': 0.0,
    'total_distance': 0.0,
    'dt': 0.0,
    'fuel_level': 100.0,
    'path_points': []
}

# Detailed update function
def update_vehicle_state(x, y, heading, velocity, rpm, 
                         steering_angle, laps, lap_distance, 
                         total_distance, dt, fuel_level=None):
    # All sensor and calculation data
```

## When to Use Each

### Use Hardware Version (Lap_map_main) When:
- ✅ Deploying to Raspberry Pi
- ✅ Racing or driving
- ✅ Need minimal distraction
- ✅ Using 5" display
- ✅ Production environment

### Use Testing Version (Map_Test) When:
- ✅ Developing new features
- ✅ Debugging issues
- ✅ Verifying formulas
- ✅ Testing without hardware
- ✅ Learning the system

## Shared Components

Both versions share:
- ✅ Same lap counting logic (`lap_counter.py`)
- ✅ Same dead reckoning formulas
- ✅ Same NumPy acceleration
- ✅ Same update rate (100 Hz)
- ✅ Same lap detection algorithm
- ✅ Same opposite direction detection

## Development Workflow

```
┌─────────────┐
│  Map_Test   │  1. Test with manual input
│  (Testing)  │  2. Verify formulas
└──────┬──────┘  3. Debug issues
       │
       ↓
┌─────────────┐
│ Lap_map_main│  4. Deploy to hardware
│ (Hardware)  │  5. Calibrate sensors
└──────┬──────┘  6. Drive and verify
       │
       ↓
┌─────────────┐
│  Iterate    │  7. Fix issues in test
│             │  8. Redeploy to hardware
└─────────────┘
```

## Performance Comparison

| Metric | Hardware | Testing |
|--------|----------|---------|
| Update Rate | 100 Hz | 100 Hz |
| Dashboard Update | 10 Hz | 10 Hz |
| Memory Usage | ~50MB | ~40MB |
| CPU Usage | ~5% | ~3% |
| Startup Time | ~3s | ~2s |

## File Size Comparison

| File | Hardware | Testing |
|------|----------|---------|
| main.py | ~5 KB | ~4 KB |
| web_dashboard.py | ~3 KB | ~8 KB |
| HTML (embedded) | ~2 KB | ~6 KB |
| Total | ~10 KB | ~18 KB |

## Configuration Differences

### Hardware (Lap_map_main/config.py)
```python
MAGNETS_PER_REVOLUTION = 18
WHEEL_DIAMETER_M = 0.2
WHEEL_CIRCUMFERENCE_M = 0.628
HALL_SENSOR_PIN = 17
AS5600_I2C_ADDRESS = 0x36
FUEL_SENSOR_PIN = 27
DASHBOARD_PORT = 5000
```

### Testing (Map_Test/config.py)
```python
# No hardware configuration needed
DASHBOARD_PORT = 5001
# All other settings same
```

## Summary

**Hardware Version**: Minimal, focused, production-ready  
**Testing Version**: Detailed, comprehensive, development-friendly

Both use the same core logic, ensuring what you test is what you deploy!
