# Dead Reckoning System - Complete Index

## 🚀 Quick Access

| What You Need | File to Read |
|---------------|--------------|
| Start testing NOW | [QUICK_START.md](QUICK_START.md) |
| Complete testing guide | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| System overview | [TESTER_SUMMARY.md](TESTER_SUMMARY.md) |
| Hardware deployment | [README.md](README.md) |
| Features checklist | [FEATURES_CHECKLIST.md](FEATURES_CHECKLIST.md) |

## 📁 File Organization

### Testing Server Files
- **web_tester.py** - Main testing server (simulates sensors)
- **templates/test_dashboard.html** - Professional testing interface
- **templates/display_5inch.html** - Hardware display simulator
- **start_tester.sh** - Linux/Mac launch script
- **start_tester.bat** - Windows launch script

### Hardware Deployment Files
- **main.py** - Production system (real sensors)
- **sensors.py** - AS5600 and AS314 sensor interfaces
- **lap_counter.py** - Lap counting logic
- **pi_filter.py** - PI filter implementation
- **web_dashboard.py** - Hardware dashboard
- **templates/dashboard.html** - Hardware display

### Configuration
- **config.py** - All system parameters

### Utilities
- **visualize_path.py** - Plot recorded paths

### Documentation

#### Getting Started
- **QUICK_START.md** - Quick reference card
- **TESTING_GUIDE.md** - Complete testing guide
- **README.md** - Hardware deployment guide

#### System Information
- **TESTER_SUMMARY.md** - Testing server overview
- **SYSTEM_ARCHITECTURE.md** - Architecture diagrams
- **FEATURES_CHECKLIST.md** - Requirements verification

#### Technical Details
- **FORMULAS.md** - Mathematical formulas
- **TIMING_ARCHITECTURE.md** - Hardware interrupts
- **ERROR_MANAGEMENT.md** - Error reduction strategies
- **PI_FILTER_GUIDE.md** - PI filter explanation
- **INTEGRATION_METHODS.md** - Integration methods
- **PERFORMANCE_AND_TIMING.md** - Performance analysis
- **FORMULA_CLARIFICATION.md** - Formula clarifications

## 🎯 Usage Workflows

### Testing Workflow
1. Read [QUICK_START.md](QUICK_START.md)
2. Run `python web_tester.py`
3. Open http://localhost:8000
4. Select a test track
5. Click "Start Test"
6. Verify results

### Hardware Deployment Workflow
1. Test with web_tester.py first
2. Read [README.md](README.md)
3. Connect sensors (AS5600, AS314)
4. Run `python main.py`
5. Calibrate sensors
6. Start driving

### Learning Workflow
1. Read [TESTER_SUMMARY.md](TESTER_SUMMARY.md)
2. Read [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
3. Read [FORMULAS.md](FORMULAS.md)
4. Read [PI_FILTER_GUIDE.md](PI_FILTER_GUIDE.md)
5. Experiment with test tracks

## 📊 Key Concepts

### Dead Reckoning
- Calculate position from velocity and heading
- No GPS needed
- Accumulates error over time
- See: [FORMULAS.md](FORMULAS.md)

### Sensors
- **AS5600**: Magnetic encoder for steering angle
- **AS314**: Hall effect sensor for RPM
- See: [sensors.py](sensors.py)

### Error Reduction
- **PI Filter**: Smooths sensor noise (50% reduction)
- **RK2 Integration**: Accurate turns (70% reduction)
- **Lap Reset**: Prevents accumulation
- See: [ERROR_MANAGEMENT.md](ERROR_MANAGEMENT.md)

### Lap Counting
- Detects return to start position
- Minimum lap distance (10m)
- Opposite direction detection
- See: [lap_counter.py](lap_counter.py)

## 🔧 Configuration Parameters

### Key Settings (config.py)
```python
WHEEL_CIRCUMFERENCE_M = 0.628    # Adjust to your wheel
UPDATE_RATE_HZ = 100             # Sensor update rate
ENABLE_PI_FILTER = True          # Steering smoothing
USE_RK2_INTEGRATION = True       # Better accuracy
ENABLE_LAP_RESET = True          # Prevent error accumulation
```

### Testing Settings (web_tester.py)
```python
dt = 0.2                         # Fixed update interval
start_position = (0, 0)          # Starting point
initial_heading = 0              # Initial direction
```

## 📈 Performance Expectations

### Testing Server
- Update rate: 5 Hz (dt=0.2s)
- Display rate: 10 Hz
- Expected error: 0.5-3m per lap
- Lap detection: < 2m from start

### Hardware System
- Update rate: 100 Hz (10ms)
- Display rate: 2 Hz
- Expected error: 0.5-3m per lap
- Hardware interrupts: < 0.01ms timing

## 🎓 Documentation by Topic

### For Beginners
1. [QUICK_START.md](QUICK_START.md) - Get started fast
2. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Learn to test
3. [TESTER_SUMMARY.md](TESTER_SUMMARY.md) - Understand system

### For Developers
1. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - System design
2. [FORMULAS.md](FORMULAS.md) - Math details
3. [PI_FILTER_GUIDE.md](PI_FILTER_GUIDE.md) - Filter theory

### For Hardware Engineers
1. [README.md](README.md) - Hardware setup
2. [TIMING_ARCHITECTURE.md](TIMING_ARCHITECTURE.md) - Interrupts
3. [ERROR_MANAGEMENT.md](ERROR_MANAGEMENT.md) - Error handling

### For Troubleshooting
1. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing issues
2. [README.md](README.md) - Hardware issues
3. [ERROR_MANAGEMENT.md](ERROR_MANAGEMENT.md) - Error analysis

## 🌐 Web Interfaces

### Testing Server (port 8888)
- **Main Dashboard**: http://127.0.0.1:8888
  - Track selection
  - 2D path visualization
  - Complete data display
  - Control buttons

- **5" Display**: http://127.0.0.1:8888/display
  - Simulates hardware display
  - Shows: velocity, lap distance, total distance
  - 800x480 resolution

### Hardware System (port 5000)
- **Dashboard**: http://localhost:5000
  - Real-time path
  - Lap counter
  - Fuel indicator
  - Minimal display for 5" screen

## 🔍 Troubleshooting Index

| Problem | Solution File |
|---------|---------------|
| Testing server won't start | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Path not updating | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Lap not counting | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Excessive error | [ERROR_MANAGEMENT.md](ERROR_MANAGEMENT.md) |
| Sensor not detected | [README.md](README.md) |
| Hardware issues | [README.md](README.md) |

## 📦 Dependencies

```
numpy>=1.24.0
RPi.GPIO>=0.7.1          # Hardware only
smbus2>=0.4.2            # Hardware only
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0
```

Install: `pip install -r requirements.txt`

## 🎯 Test Tracks

| Track | Duration | Best For |
|-------|----------|----------|
| Circle | 60s | Basic verification |
| Oval | 80s | Lap counting |
| Figure-8 | 100s | Complex patterns |
| Slalom | 60s | Steering filter |
| High-Speed | 50s | Speed accuracy |

## ✅ Verification Checklist

- [ ] Read QUICK_START.md
- [ ] Start testing server
- [ ] Test all 5 tracks
- [ ] Verify lap counting
- [ ] Check error values
- [ ] Review 5" display output
- [ ] Read README.md for hardware
- [ ] Deploy to Raspberry Pi
- [ ] Connect sensors
- [ ] Run hardware tests
- [ ] Compare with simulation

## 📞 Support Resources

### Documentation
- All .md files in this directory
- Comments in Python files
- Inline documentation

### Testing
- Use web_tester.py for safe testing
- No hardware needed
- Fast iteration

### Hardware
- Follow README.md carefully
- Test sensors individually
- Use hardware interrupts

## 🎉 Quick Commands

### Start Testing
```bash
# Windows
start_tester.bat

# Linux/Mac
./start_tester.sh

# Manual
python web_tester.py
```

### Start Hardware
```bash
python main.py
```

### Visualize Path
```bash
python visualize_path.py
```

## 📝 Summary

This system provides:
- ✅ Complete testing environment
- ✅ Hardware deployment code
- ✅ Comprehensive documentation
- ✅ Professional interfaces
- ✅ Error reduction strategies
- ✅ Lap counting logic
- ✅ 5" display support

**Start here**: [QUICK_START.md](QUICK_START.md)

**Questions?** Check the relevant documentation file above.

---

**Ready to test!** Run `python web_tester.py` and open http://127.0.0.1:8888
