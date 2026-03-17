# Quick Start Guide

## 🧪 Testing First (Recommended)

### 1. Test with Manual Input
```bash
cd Map_Test
pip install -r requirements.txt
python3 main.py
```

### 2. Open Browser
Navigate to: `http://localhost:5001`

### 3. Test Scenarios

**Straight Line:**
- Steering: 0°
- Velocity: 5 m/s
- Watch vehicle move straight

**Turn Right:**
- Steering: 15°
- Velocity: 5 m/s
- Watch vehicle turn

**Complete a Lap:**
- Drive in a circle back to (0, 0)
- Lap counter increments when within 2m of start

**Opposite Direction:**
- Complete lap clockwise
- Complete lap counter-clockwise
- Console shows "(OPPOSITE DIRECTION)"

## 🏎️ Hardware Deployment

### 1. Hardware Connections

**AS5600 (Steering Angle Sensor):**
- VCC → 3.3V
- GND → GND
- SDA → GPIO 2 (I2C SDA)
- SCL → GPIO 3 (I2C SCL)

**AS314 (Hall Effect Sensor):**
- VCC → 3.3V
- GND → GND
- OUT → GPIO 17

**Fuel Sensor (Optional):**
- Connect to GPIO 27 (or configure in config.py)

**5" Display:**
- Connect via HDMI or DSI

### 2. Enable I2C
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

### 3. Verify Sensors
```bash
# Check I2C devices
i2cdetect -y 1
# Should show 0x36 for AS5600

# Test GPIO
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"
```

### 4. Install Dependencies
```bash
cd Lap_map_main
pip install -r requirements.txt
```

### 5. Configure
Edit `config.py`:
```python
WHEEL_DIAMETER_M = 0.2  # Your wheel diameter
HALL_SENSOR_PIN = 17    # Your GPIO pin
FUEL_SENSOR_PIN = 27    # Your fuel sensor pin
```

### 6. Run
```bash
python3 main.py
```

### 7. Open Dashboard
On the 5" display, open browser to: `http://localhost:5000`

### 8. Calibrate
- Position vehicle pointing straight
- Press Enter when prompted
- Start driving!

## 📊 What You'll See

### Hardware Display (5" Screen)
- **Map**: Full screen path visualization
- **Lap Counter**: Top right (large numbers)
- **Current Position**: Pulsing green circle
- **Fuel Level**: Bottom right with color bar

### Testing Display (Full Screen)
- **All sensor readings**
- **Calculation steps**
- **Manual input controls**
- **Detailed metrics**

## 🔧 Troubleshooting

### Sensors Not Working
```bash
# Check I2C
i2cdetect -y 1

# Check GPIO permissions
sudo usermod -a -G gpio $USER
# Logout and login again
```

### Dashboard Not Loading
```bash
# Check if port is in use
netstat -tuln | grep 5000

# Try different port in config.py
DASHBOARD_PORT = 5001
```

### Lap Not Counting
- Ensure you return within 2m of start (0, 0)
- Check console for lap messages
- Verify minimum lap distance (10m default)

## 📝 Key Formulas

### Velocity from RPM
```
velocity = (RPM / 60) * wheel_circumference
```

### Position Update (Straight)
```
dx = velocity * Δt * cos(heading)
dy = velocity * Δt * sin(heading)
```

### Position Update (Turning)
```
heading_rate = (velocity * tan(steering)) / wheelbase
heading += heading_rate * Δt
dx = velocity * Δt * cos(heading)
dy = velocity * Δt * sin(heading)
```

## 🎯 Next Steps

1. ✅ Test in Map_Test folder
2. ✅ Connect hardware sensors
3. ✅ Run Lap_map_main on Raspberry Pi
4. ✅ Calibrate sensors
5. ✅ Drive and verify lap counting
6. ⏳ Implement fuel sensor (optional)
7. ⏳ Fine-tune parameters

## 📚 Documentation

- `SYSTEM_OVERVIEW.md`: Complete system architecture
- `Lap_map_main/FORMULAS.md`: Mathematical formulas
- `Lap_map_main/README.md`: Hardware documentation
- `Map_Test/README.md`: Testing documentation

## 🚀 Performance

- Update Rate: 100 Hz (10ms)
- Dashboard: 10 Hz (100ms)
- NumPy Acceleration: ~10x faster
- Memory: ~50MB

## ⚡ Tips

1. **Test first**: Always test in Map_Test before hardware
2. **Calibrate**: Calibrate steering sensor when vehicle is straight
3. **Wheel diameter**: Measure accurately for correct velocity
4. **Magnet spacing**: 18 magnets = 20° spacing
5. **Start position**: Always start at (0, 0) for lap counting

## 🆘 Need Help?

Check the detailed documentation:
- Hardware issues → `Lap_map_main/README.md`
- Testing issues → `Map_Test/README.md`
- Formula questions → `Lap_map_main/FORMULAS.md`
- System overview → `SYSTEM_OVERVIEW.md`
