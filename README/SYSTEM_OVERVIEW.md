# Dead Reckoning System - Complete Overview

## Project Structure

```
gokart/
├── Lap_map_main/          # HARDWARE VERSION (Raspberry Pi 5)
│   ├── main.py            # Hardware sensors (AS5600 + AS314)
│   ├── sensors.py         # Sensor interface classes
│   ├── lap_counter.py     # Lap counting logic
│   ├── web_dashboard.py   # Minimal dashboard (FastAPI)
│   ├── config.py          # Hardware configuration
│   ├── FORMULAS.md        # Mathematical formulas
│   └── README.md          # Hardware documentation
│
└── Map_Test/              # TESTING VERSION (Manual Input)
    ├── main.py            # Manual sensor input
    ├── lap_counter.py     # Same lap counting logic
    ├── web_dashboard.py   # Detailed dashboard (FastAPI)
    ├── config.py          # Test configuration
    └── README.md          # Testing documentation
```

## Key Differences

| Feature | Lap_map_main (Hardware) | Map_Test (Testing) |
|---------|------------------------|-------------------|
| **Purpose** | Production on Raspberry Pi | Testing with manual input |
| **Sensors** | AS5600 + AS314 hardware | Manual web input |
| **Display** | 5" screen (800x480) | Full screen browser |
| **Dashboard** | Minimal (map + laps + fuel) | Detailed (all metrics) |
| **Port** | 5000 | 5001 |
| **Shows** | Map, Lap (top right), Position circle, Fuel | All sensor data, calculations, formulas |

## Hardware Version (Lap_map_main)

### Display Layout (5" Screen)
```
┌─────────────────────────────────────────┐
│                                  ┌────┐ │
│                                  │LAP │ │ ← Top Right
│                                  │ 3  │ │
│                                  └────┘ │
│                                         │
│         [Vehicle Path Map]              │
│                                         │
│              ●  ← Current Position      │
│             (pulsing circle)            │
│                                         │
│                                         │
│                                  ┌────┐ │
│                                  │FUEL│ │ ← Bottom Right
│                                  │▓▓▓▓│ │
│                                  │75% │ │
│                                  └────┘ │
└─────────────────────────────────────────┘
```

### Features
- Clean, minimal interface for driving
- Large lap counter (easy to read while driving)
- Pulsing circle shows current position
- Fuel bar with color coding (green/yellow/red)
- Auto-scaling map

### Run Hardware Version
```bash
cd Lap_map_main
pip install -r requirements.txt
python3 main.py
# Open http://localhost:5000 on 5" display
```

## Testing Version (Map_Test)

### Display Layout (Full Screen)
```
┌─────────────────────────────────────────────────────────┐
│  🧪 VEHICLE TESTING DASHBOARD                           │
├─────────────────────────────────────────────────────────┤
│  MANUAL INPUT CONTROLS                                  │
│  [Steering: 0°] [Velocity: 0 m/s] [Fuel: 100%]         │
│  [UPDATE SENSORS] [RESET POSITION]                      │
├──────────────────────┬──────────────────────────────────┤
│ SENSOR INPUTS        │                           ┌────┐ │
│ • SAS: 0.0°          │                           │LAP │ │
│ • Velocity: 0.00 m/s │                           │ 0  │ │
│ • RPM: 0 rpm         │                           └────┘ │
│ • Fuel: 100%         │                                  │
│                      │    [Vehicle Path Map]            │
│ CALCULATIONS         │                                  │
│ • Δt: 0.010 s        │         ●  ← Position            │
│ • Heading: 0.0°      │                                  │
│ • Distance: 0.000 m  │                                  │
│                      │                                  │
│ POSITION & DISTANCE  │                                  │
│ • X: 0.00 m          │                                  │
│ • Y: 0.00 m          │                                  │
│ • Current Lap: 0.0 m │                                  │
│ • Total: 0.0 m       │                                  │
└──────────────────────┴──────────────────────────────────┘
```

### Features
- Manual input controls for testing
- Shows all sensor readings
- Displays calculation steps (Δt, heading, distance)
- Real-time position tracking
- Same lap counting logic as hardware

### Run Testing Version
```bash
cd Map_Test
pip install -r requirements.txt
python3 main.py
# Open http://localhost:5001 in browser
```

## Dead Reckoning Formulas

### 1. Velocity from RPM
```
velocity = (RPM / 60) * wheel_circumference
RPM = (pulse_count / 18) * (60 / Δt)
```

### 2. Linear Motion (Straight)
```
displacement = velocity * Δt
dx = displacement * cos(heading)
dy = displacement * sin(heading)
position = position + [dx, dy]
```

### 3. Circular Motion (Turning)
```
heading_rate = (velocity * tan(steering_angle)) / wheelbase
heading = heading + heading_rate * Δt
displacement = velocity * Δt
dx = displacement * cos(heading)
dy = displacement * sin(heading)
position = position + [dx, dy]
```

See `Lap_map_main/FORMULAS.md` for complete details.

## Lap Counting Logic

1. **First Lap**: Learn reference path
2. **Detection**: Monitor distance from start (< 2m threshold)
3. **Validation**: Minimum 10m traveled
4. **Opposite Direction**: Compare approach vectors
   - dot_product < -0.5 → opposite direction

## Fuel Sensor Integration

### Hardware (Lap_map_main)
Edit `main.py` method `_read_fuel_level()`:

```python
def _read_fuel_level(self):
    # Example for MCP3008 ADC
    from spidev import SpiDev
    spi = SpiDev()
    spi.open(0, 0)
    raw = spi.xfer2([1, (8 + 0) << 4, 0])
    value = ((raw[1] & 3) << 8) + raw[2]
    return (value / 1023.0) * 100
```

### Testing (Map_Test)
Use the fuel slider in the web interface.

## Workflow

### Development Workflow
1. **Test in Map_Test**: Verify logic with manual input
2. **Deploy to Lap_map_main**: Run on hardware
3. **Iterate**: Fix issues in test, redeploy

### Testing Scenarios
1. Straight line motion
2. Circular paths
3. Lap completion
4. Opposite direction detection
5. Fuel level changes

## Hardware Requirements

- Raspberry Pi 5 8GB
- AS5600 magnetic encoder (I2C address 0x36)
- AS314 hall effect sensor (GPIO pin 17)
- 18 magnets (20° spacing) on wheel
- 5" display (800x480)
- Fuel sensor (GPIO pin 27, optional)

## Software Stack

- Python 3.9+
- NumPy (C-accelerated calculations)
- FastAPI (web server)
- WebSocket (real-time updates)
- RPi.GPIO (hardware interface)
- smbus2 (I2C communication)

## Performance

- Update rate: 100 Hz (10ms per cycle)
- Dashboard: 10 Hz (100ms updates)
- NumPy acceleration: ~10x faster than pure Python
- Memory: ~50MB

## Next Steps

1. **Test System**: Run Map_Test and verify formulas
2. **Hardware Setup**: Connect sensors to Raspberry Pi
3. **Calibration**: Run hardware version and calibrate
4. **Fuel Sensor**: Implement fuel reading based on your sensor
5. **Fine-tune**: Adjust wheelbase, thresholds, etc.

## Support Files

- `Lap_map_main/FORMULAS.md`: Complete mathematical documentation
- `Lap_map_main/README.md`: Hardware version guide
- `Map_Test/README.md`: Testing version guide
- Both versions use same lap counting logic
- FastAPI for both (replaced Flask)
