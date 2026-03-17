# Go-Kart Dead Reckoning System

Complete dead reckoning navigation system for go-kart with lap counting, optimized for Raspberry Pi 5 with 5" display.

## 🎯 Features

✅ **Dead Reckoning Navigation** - Position tracking using steering angle + velocity  
✅ **Automatic Lap Counting** - Detects lap completion and opposite direction  
✅ **Real-time Dashboard** - FastAPI + WebSocket for live updates  
✅ **Hardware Optimized** - Minimal 5" display (map + laps + fuel only)  
✅ **Testing Suite** - Manual input testing before hardware deployment  
✅ **NumPy Accelerated** - 100 Hz update rate with C-level performance  
✅ **Fuel Monitoring** - Placeholder for fuel sensor integration  

## 📁 Project Structure

```
gokart/
├── Lap_map_main/          # 🏎️ HARDWARE VERSION (Raspberry Pi 5)
│   ├── main.py            # Hardware sensors (AS5600 + AS314)
│   ├── sensors.py         # Sensor interfaces
│   ├── web_dashboard.py   # Minimal dashboard (5" display)
│   ├── config.py          # Hardware configuration
│   ├── FORMULAS.md        # Mathematical documentation
│   └── README.md          # Hardware guide
│
├── Map_Test/              # 🧪 TESTING VERSION (Manual Input)
│   ├── main.py            # Manual sensor simulation
│   ├── web_dashboard.py   # Detailed testing dashboard
│   ├── config.py          # Test configuration
│   └── README.md          # Testing guide
│
├── QUICK_START.md         # ⚡ Quick start guide
├── SYSTEM_OVERVIEW.md     # 📚 Complete system documentation
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Test First (Recommended)
```bash
cd Map_Test
pip install -r requirements.txt
python3 main.py
# Open http://localhost:5001
```

### 2. Deploy to Hardware
```bash
cd Lap_map_main
pip install -r requirements.txt
python3 main.py
# Open http://localhost:5000 on 5" display
```

See `QUICK_START.md` for detailed instructions.

## 🖥️ Display Comparison

### Hardware (Lap_map_main) - 5" Display
```
┌─────────────────────────────┐
│                      ┌────┐ │
│                      │LAP │ │ ← Top Right
│                      │ 3  │ │
│                      └────┘ │
│    [Vehicle Path Map]       │
│         ●  ← Position        │
│                      ┌────┐ │
│                      │FUEL│ │ ← Bottom Right
│                      │▓▓▓▓│ │
│                      └────┘ │
└─────────────────────────────┘
```
**Shows:** Map, Lap count, Position circle, Fuel level

### Testing (Map_Test) - Full Screen
```
┌──────────────────────────────────┐
│ Manual Input Controls            │
│ [Steering] [Velocity] [Fuel]     │
├──────────────┬───────────────────┤
│ Sensor Data  │  ┌────┐           │
│ Calculations │  │LAP │  [Map]    │
│ Position     │  └────┘           │
│ Distance     │      ●            │
└──────────────┴───────────────────┘
```
**Shows:** All sensor data, calculations, detailed metrics

## 🔧 Hardware Requirements

- **Raspberry Pi 5 8GB**
- **AS5600** - Magnetic encoder for steering angle (I2C)
- **AS314** - Hall effect sensor for RPM (GPIO)
- **18 Magnets** - 20° spacing on wheel
- **5" Display** - 800x480 resolution
- **Fuel Sensor** - Optional (GPIO)

## 📊 Key Formulas

### Velocity from RPM
```
velocity = (RPM / 60) × wheel_circumference
RPM = (pulses / 18) × (60 / Δt)
```

### Dead Reckoning (Straight)
```
dx = velocity × Δt × cos(heading)
dy = velocity × Δt × sin(heading)
```

### Dead Reckoning (Turning)
```
heading_rate = (velocity × tan(steering)) / wheelbase
heading += heading_rate × Δt
dx = velocity × Δt × cos(heading)
dy = velocity × Δt × sin(heading)
```

See `Lap_map_main/FORMULAS.md` for complete documentation.

## 🏁 Lap Counting Logic

1. **First Lap**: Learn reference path
2. **Detection**: Monitor distance from start (< 2m)
3. **Validation**: Minimum 10m traveled
4. **Opposite Direction**: Compare approach vectors
   - dot_product < -0.5 → opposite direction detected

## 🎨 Dashboard Features

### Hardware Dashboard (Minimal)
- Full-screen map visualization
- Large lap counter (top right)
- Pulsing position indicator
- Color-coded fuel bar (green/yellow/red)
- Auto-scaling map

### Testing Dashboard (Detailed)
- Manual input controls
- All sensor readings
- Calculation steps (Δt, heading, distance)
- Real-time position tracking
- Same lap logic as hardware

## 📈 Performance

- **Update Rate**: 100 Hz (10ms per cycle)
- **Dashboard**: 10 Hz (100ms updates)
- **NumPy Acceleration**: ~10x faster than pure Python
- **Memory Usage**: ~50MB

## 🔌 Fuel Sensor Integration

### Placeholder Implementation
Currently returns 100%. To implement:

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

## 📚 Documentation

- **QUICK_START.md** - Get started in 5 minutes
- **SYSTEM_OVERVIEW.md** - Complete architecture
- **Lap_map_main/FORMULAS.md** - Mathematical formulas
- **Lap_map_main/README.md** - Hardware version guide
- **Map_Test/README.md** - Testing version guide

## 🛠️ Development Workflow

1. **Test** in Map_Test with manual input
2. **Verify** formulas and lap counting
3. **Deploy** to Lap_map_main on hardware
4. **Calibrate** sensors
5. **Drive** and monitor

## ⚡ Technology Stack

- **Python 3.9+** - Main language
- **NumPy** - Fast C-level calculations
- **FastAPI** - Modern web framework
- **WebSocket** - Real-time updates
- **RPi.GPIO** - Hardware interface
- **smbus2** - I2C communication

## 🎯 Use Cases

1. **Go-Kart Racing** - Track laps and position
2. **Testing** - Verify vehicle dynamics
3. **Data Logging** - Record path and performance
4. **Navigation** - Real-time position tracking

## 🔍 Troubleshooting

### Sensors Not Detected
```bash
i2cdetect -y 1  # Should show 0x36
```

### Dashboard Not Loading
```bash
netstat -tuln | grep 5000  # Check port
```

### Lap Not Counting
- Return within 2m of start (0, 0)
- Travel minimum 10m
- Check console for messages

## 📝 Configuration

Edit `config.py` in respective folder:

```python
# Hardware
WHEEL_DIAMETER_M = 0.2
HALL_SENSOR_PIN = 17
FUEL_SENSOR_PIN = 27
DASHBOARD_PORT = 5000

# Testing
DASHBOARD_PORT = 5001
```

## 🚦 Status

- ✅ Dead reckoning implementation
- ✅ Lap counting with opposite direction detection
- ✅ Hardware dashboard (minimal for 5" display)
- ✅ Testing dashboard (detailed for development)
- ✅ FastAPI web server
- ✅ NumPy acceleration
- ⏳ Fuel sensor (placeholder ready)

## 📄 License

This project is for educational and personal use.

## 🤝 Contributing

1. Test changes in Map_Test first
2. Verify formulas in FORMULAS.md
3. Update documentation
4. Test on hardware

## 📞 Support

Check documentation files for detailed help:
- Hardware issues → `Lap_map_main/README.md`
- Testing issues → `Map_Test/README.md`
- Formula questions → `Lap_map_main/FORMULAS.md`

---

**Made for Raspberry Pi 5 with ❤️**
