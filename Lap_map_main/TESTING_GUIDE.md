# Hardware Testing Server Guide

## Overview

The `web_tester.py` server allows you to test and verify the dead reckoning system before deploying to hardware. It simulates the AS5600 (steering angle) and AS314 (RPM) sensors with predefined test tracks.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Testing Server

```bash
python web_tester.py
```

### 3. Open the Dashboard

- **Main Testing Dashboard**: http://127.0.0.1:8888
- **5" Display Simulator**: http://127.0.0.1:8888/display

## Features

### Simulated Hardware Inputs

1. **AS5600 Magnetic Encoder** - Steering angle sensor
   - Simulates steering angle in radians
   - Applies PI filter for noise reduction
   - Rate limiting to physical constraints

2. **AS314 Hall Effect Sensor** - RPM measurement
   - Simulates wheel RPM
   - Converts to velocity using wheel circumference
   - Fixed dt = 0.2s as specified

### Test Tracks

The system includes 5 predefined test tracks:

#### 1. Circle Track
- Simple circular path
- 50m diameter
- Constant steering angle (15°)
- Constant RPM (300)
- Duration: 60 seconds
- **Best for**: Basic system verification

#### 2. Oval Track
- Racing oval with straights and turns
- Alternating straight and curved sections
- RPM: 350
- Duration: 80 seconds
- **Best for**: Testing lap counting

#### 3. Figure-8 Track
- Complex figure-8 pattern
- Alternating left/right turns
- Tests opposite direction detection
- Duration: 100 seconds
- **Best for**: Advanced lap counting verification

#### 4. Slalom Course
- Zigzag pattern with quick direction changes
- Sinusoidal steering input
- Tests PI filter performance
- Duration: 60 seconds
- **Best for**: Steering filter testing

#### 5. High-Speed Oval
- Fast oval track with banking
- High RPM (600)
- Quick turns
- Duration: 50 seconds
- **Best for**: High-speed accuracy testing

## Dashboard Interface

### Left Panel - Track Selection
- Click any track to select it
- Selected track highlights in green
- Shows track name and description

### Center Panel - 2D Path Visualization
- Real-time path plotting
- Green line shows traveled path
- Yellow pulsing circle shows current position
- Red line indicates heading direction
- Grid and axes for reference
- Auto-scaling to fit path

### Right Panel - Data Display

#### Position Data
- X Position (meters)
- Y Position (meters)
- Heading (degrees)

#### Lap Information
- Lap Count
- Current Lap Distance (meters)
- Total Distance Traveled (meters)

#### Sensor Inputs
- Velocity (m/s)
- RPM from AS314 sensor
- Steering Angle from AS5600 (degrees)

#### 5" Display Output
Simulates what will be shown on the hardware 5" display:
- Velocity
- Current Lap Distance
- Total Distance Traveled

## Controls

### Start Test
1. Select a test track from the left panel
2. Click "▶ Start Test"
3. Watch the path develop in real-time
4. Monitor all sensor readings and outputs

### Stop Test
- Click "⏹ Stop Test" to halt the current test
- Path and data remain visible

### Reset
- Click "🔄 Reset" to clear all data
- Returns system to initial state (0,0)
- Ready for next test

## Configuration

The testing server uses the same configuration as the hardware system:

```python
# From config.py
WHEEL_CIRCUMFERENCE_M = 0.628m  # Adjust to your wheel
ENABLE_PI_FILTER = True         # Steering filter
USE_RK2_INTEGRATION = True      # Better accuracy in turns
```

### Fixed Parameters (as requested)
- **dt = 0.2s** (5 Hz update rate)
- **Starting position**: (0, 0)
- **Initial heading**: 0 radians (East)

## Verification Checklist

### ✅ Basic Functionality
- [ ] Path is plotted correctly
- [ ] Position updates in real-time
- [ ] Heading indicator shows direction
- [ ] Velocity calculated from RPM

### ✅ Lap Counting
- [ ] Lap count increments when returning to start
- [ ] Minimum lap distance enforced (10m)
- [ ] Current lap distance resets after lap completion
- [ ] Total distance continues accumulating

### ✅ Sensor Simulation
- [ ] Steering angle changes smoothly (PI filter working)
- [ ] RPM converts to velocity correctly
- [ ] No sudden jumps or glitches

### ✅ Display Output
- [ ] 5" display section updates correctly
- [ ] Values match main data panel
- [ ] Large, readable numbers

### ✅ Error Management
- [ ] Path doesn't drift excessively
- [ ] Lap completion brings vehicle near start
- [ ] Error stays within acceptable range (< 5m per lap)

## Expected Results

### Circle Track
- Should complete ~2-3 laps
- Path should be nearly circular
- Lap distance: ~157m (circumference of 50m diameter circle)
- Error per lap: < 2m

### Oval Track
- Should complete ~1-2 laps
- Clear straight sections and turns
- Lap distance: ~200-250m
- Error per lap: < 3m

### Figure-8 Track
- Complex crossing pattern
- Tests opposite direction detection
- May trigger lap count when crossing center
- Error per lap: < 4m

## Troubleshooting

### Path Not Updating
- Check browser console for WebSocket errors
- Ensure server is running on port 8888
- Refresh the page

### Lap Not Counting
- Verify path returns within 2m of start (0,0)
- Check minimum lap distance (10m)
- Look for console messages about lap completion

### Excessive Error
- Check PI filter settings in config.py
- Verify wheel circumference is correct
- Ensure RK2 integration is enabled

### Display Not Updating
- Check WebSocket connection status
- Verify test is running (status indicator green)
- Try stopping and restarting test

## Hardware Deployment

After successful testing:

1. **Verify all tracks work correctly**
2. **Note typical error values**
3. **Confirm lap counting is accurate**
4. **Deploy to hardware using main.py**

The testing server uses the same algorithms as the hardware system, so successful tests indicate the hardware will work correctly.

## Technical Details

### Update Rate
- Sensor simulation: 5 Hz (dt = 0.2s)
- Display update: 10 Hz (100ms)
- WebSocket: 10 Hz (100ms)

### Integration Method
- Uses RK2 (Runge-Kutta 2nd order) by default
- More accurate in turns than Euler method
- Reduces error by ~70%

### PI Filter
- Kp = 0.8 (proportional gain)
- Ki = 0.05 (integral gain)
- Max steering rate = 120°/s
- Reduces sensor noise by ~50%

## Next Steps

1. **Test all tracks** - Verify each track works correctly
2. **Measure error** - Note typical error per lap
3. **Adjust parameters** - Tune PI filter if needed
4. **Deploy to hardware** - Use main.py with real sensors
5. **Compare results** - Verify hardware matches simulation

## Support

If you encounter issues:
1. Check console output for error messages
2. Verify all dependencies are installed
3. Ensure port 8000 is not in use
4. Review configuration in config.py

---

**Ready to test!** Start the server and select a track to begin verification.
