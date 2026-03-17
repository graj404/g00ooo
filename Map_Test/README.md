# Dead Reckoning Testing System

Testing version with manual sensor input via web interface.

## Features

✅ Manual input for steering angle and velocity  
✅ Detailed dashboard showing all calculations  
✅ Real-time formula verification  
✅ Fuel level simulation  
✅ Same dead reckoning logic as hardware version  

## Installation

```bash
cd Map_Test
pip install -r requirements.txt
```

## Usage

1. Run the test system:
```bash
python3 main.py
```

2. Open browser: `http://localhost:5001`

3. Use the manual input controls:
   - Steering Angle: -45° to +45° (degrees)
   - Velocity: 0 to 20 m/s
   - Fuel Level: 0 to 100%

4. Click "UPDATE SENSORS" to apply changes

5. Watch the vehicle move on the map in real-time

## Dashboard Display

The testing dashboard shows:
- **Sensor Inputs**: SAS, Velocity, RPM, Fuel
- **Calculations**: Δt, Heading, Step Distance
- **Position & Distance**: X, Y, Current Lap, Total
- **Map**: Visual path with current position circle
- **Lap Counter**: Top right corner

## Testing Scenarios

### Test 1: Straight Line
- Steering: 0°
- Velocity: 5 m/s
- Expected: Vehicle moves straight in current heading direction

### Test 2: Circular Path
- Steering: 15°
- Velocity: 5 m/s
- Expected: Vehicle turns in a circle

### Test 3: Lap Completion
- Drive a closed loop returning to start (0, 0)
- Expected: Lap counter increments when within 2m of start

### Test 4: Opposite Direction
- Complete one lap clockwise
- Complete second lap counter-clockwise
- Expected: "(OPPOSITE DIRECTION)" message in console

### Test 5: Fuel Depletion
- Adjust fuel level slider
- Expected: Fuel bar color changes (green > yellow > red)

## Formulas Used

See `../Lap_map_main/FORMULAS.md` for detailed equations.

## Differences from Hardware Version

| Feature | Hardware (Lap_map_main) | Testing (Map_Test) |
|---------|------------------------|-------------------|
| Sensors | AS5600 + AS314 | Manual input |
| Dashboard | Minimal (map + laps) | Detailed (all data) |
| Port | 5000 | 5001 |
| Display | 5" (800x480) | Full screen |
| Fuel Sensor | GPIO pin | Manual slider |
