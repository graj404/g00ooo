# Dead Reckoning Vehicle Path Mapping - HARDWARE VERSION

Dead reckoning system for Raspberry Pi 5 using AS5600 magnetic encoder (steering angle) and AS314 hall effect sensor (wheel RPM).

## Features

✅ Real-time HTML dashboard optimized for 5" display (800x480)  
✅ Automatic lap counting using dead reckoning only  
✅ Detects opposite direction returns to start  
✅ Reference path learning from first lap  
✅ NumPy-accelerated calculations (100 Hz update rate)  
✅ Fuel level sensor support (placeholder for implementation)  

## Hardware Setup

- **Raspberry Pi 5 8GB**
- **AS5600**: I2C magnetic encoder for steering angle (SAS)
- **AS314**: Hall effect sensor with 18 magnets (20° spacing) for RPM
- **5" Display**: 800x480 resolution
- **Fuel Sensor**: GPIO pin (to be implemented)

## Installation

```bash
cd Lap_map_main
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to match your vehicle:
- `WHEEL_DIAMETER_M`: Your wheel diameter (default: 0.2m)
- `HALL_SENSOR_PIN`: GPIO pin for AS314 hall sensor (default: 17)
- `AS5600_I2C_ADDRESS`: I2C address for AS5600 (default: 0x36)
- `FUEL_SENSOR_PIN`: GPIO pin for fuel sensor (default: 27)
- `DASHBOARD_PORT`: Web dashboard port (default: 5000)

## Usage

1. Run the main program:
```bash
python3 main.py
```

2. Open dashboard on 5" display: `http://localhost:5000`

3. Calibrate when prompted (vehicle should be pointing straight)

4. Drive your vehicle:
   - First lap learns the reference path
   - Subsequent laps are counted automatically
   - Dashboard shows: map, lap count (top right), current position, fuel level

## Dashboard Display (5" Screen)

Minimal display optimized for driving:
- **Map**: Full screen path visualization
- **Lap Counter**: Top right corner (large, easy to read)
- **Current Position**: Pulsing green circle on map
- **Fuel Indicator**: Bottom right with color-coded bar
  - Green: > 50%
  - Yellow: 20-50%
  - Red: < 20%

## Fuel Sensor Implementation

The fuel sensor is currently a placeholder. To implement:

1. Connect your fuel sensor to GPIO pin 27 (or change in config.py)

2. Edit `main.py` method `_read_fuel_level()`:

```python
def _read_fuel_level(self):
    # Example for analog sensor with MCP3008 ADC
    from spidev import SpiDev
    spi = SpiDev()
    spi.open(0, 0)
    channel = 0  # ADC channel
    raw = spi.xfer2([1, (8 + channel) << 4, 0])
    value = ((raw[1] & 3) << 8) + raw[2]
    percentage = (value / 1023.0) * 100
    return percentage
```

## How It Works

### Dead Reckoning
- **Hall sensor** counts magnet pulses → RPM → velocity
- **AS5600** reads steering angle continuously
- **NumPy** performs fast calculations in C (100 Hz)
- Position updated using velocity and heading integration

See `FORMULAS.md` for detailed equations.

### Lap Counting (Dead Reckoning Only)
1. **First lap**: System learns reference path
2. **Lap detection**: Monitors distance from start position
3. **Validation**: Requires minimum distance traveled (10m)
4. **Opposite direction**: Detects approach vector using position history
   - Compares current approach with previous lap
   - Flags if dot product < -0.5 (opposite directions)

## Testing

Use the `Map_Test` folder for testing with manual input before deploying to hardware.

```bash
cd ../Map_Test
python3 main.py
# Open http://localhost:5001 for detailed testing dashboard
```

## Files

- `main.py`: Main dead reckoning loop with hardware sensors
- `sensors.py`: AS5600 and AS314 sensor interfaces
- `lap_counter.py`: Lap counting logic (handles opposite direction)
- `web_dashboard.py`: FastAPI web server (minimal display)
- `config.py`: Configuration parameters
- `FORMULAS.md`: Detailed mathematical formulas
- `path_log.csv`: Logged data (generated during run)

## Troubleshooting

### Sensors not detected
- Check I2C connection: `i2cdetect -y 1`
- Verify AS5600 address (should be 0x36)
- Check GPIO wiring for hall sensor

### Dashboard not loading
- Verify port 5000 is not in use: `netstat -tuln | grep 5000`
- Check firewall settings
- Try accessing from Pi itself: `http://localhost:5000`

### Lap not counting
- Ensure vehicle returns within 2m of start position
- Check minimum lap distance (10m default)
- View console for lap completion messages

## Performance

- Update rate: 100 Hz (10ms per cycle)
- Dashboard update: 10 Hz (100ms)
- NumPy acceleration: ~10x faster than pure Python
- Memory usage: ~50MB
