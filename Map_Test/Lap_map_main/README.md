# Dead Reckoning Vehicle Path Mapping

Dead reckoning system for Raspberry Pi 5 using AS5600 magnetic encoder (steering angle) and AS314 hall effect sensor (wheel RPM).

## Features

✅ Real-time HTML dashboard with live path visualization  
✅ Automatic lap counting using dead reckoning only  
✅ Detects opposite direction returns to start  
✅ Reference path learning from first lap  
✅ NumPy-accelerated calculations (100 Hz update rate)  

## Hardware Setup

- **Raspberry Pi 5 8GB**
- **AS5600**: I2C magnetic encoder for steering angle (SAS)
- **AS314**: Hall effect sensor with 18 magnets (20° spacing) for RPM

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to match your vehicle:
- `WHEEL_DIAMETER_M`: Your wheel diameter
- `HALL_SENSOR_PIN`: GPIO pin for hall sensor
- `MAGNETS_PER_REVOLUTION`: Number of magnets (18 for 20° spacing)
- `DASHBOARD_PORT`: Web dashboard port (default: 5000)

## Usage

1. Run the main program:
```bash
python3 main.py
```

2. Open dashboard in browser: `http://raspberry-pi-ip:5000`

3. Calibrate when prompted (vehicle should be pointing straight)

4. Drive your vehicle:
   - First lap learns the reference path
   - Subsequent laps are counted automatically
   - Dashboard shows live position, velocity, heading, and lap count

5. Visualize recorded path:
```bash
python3 visualize_path.py
```

## How It Works

### Dead Reckoning
- **Hall sensor** counts magnet pulses → RPM → velocity
- **AS5600** reads steering angle continuously
- **NumPy** performs fast calculations in C (100 Hz)
- Position updated using velocity and heading integration

### Lap Counting (Dead Reckoning Only)
1. **First lap**: System learns reference path
2. **Lap detection**: Monitors distance from start position
3. **Validation**: Requires minimum distance traveled
4. **Opposite direction**: Detects approach vector using position history
   - Compares current approach with previous lap
   - Flags if dot product < -0.5 (opposite directions)

### Web Dashboard
- Real-time updates at 10 Hz via WebSocket
- Live path visualization with auto-scaling
- Displays: position, heading, velocity, RPM, steering angle
- Lap counter with current/total distance

## Files

- `main.py`: Main dead reckoning loop with lap counting
- `sensors.py`: AS5600 and AS314 sensor interfaces
- `lap_counter.py`: Lap counting logic (handles opposite direction)
- `web_dashboard.py`: Flask/SocketIO web server
- `templates/dashboard.html`: Real-time HTML dashboard
- `config.py`: Configuration parameters
- `visualize_path.py`: Plot recorded path
- `path_log.csv`: Logged data (generated during run)
