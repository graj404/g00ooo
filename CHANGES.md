# Changes Made - IR Sensor & Fuel Sensor Integration

## Summary
Replaced Hall effect sensor with IR sensor and integrated fuel level monitoring using ADS1115 ADC. All code updated to Python 3 with HTML dashboard.

## Hardware Changes

### Removed
- AS314 Hall Effect Sensor (GPIO 17)
- RPi.GPIO library

### Added
- IR Sensor (GPIO 27) - for RPM/RPS measurement
- ADS1115 ADC (I2C) - for analog fuel sensor reading
- Fuel level sensor (analog, connected to ADS1115 A0)

## Software Changes

### 1. sensors.py
- Replaced `HallEffectSensor` class with `IRSensor` class
  - Uses gpiozero library instead of RPi.GPIO
  - Implements pulse counting in background thread
  - Calculates RPS and RPM from pulse count
  - GPIO pin changed to 27

- Added `FuelSensor` class
  - Reads analog voltage from ADS1115 ADC
  - Converts voltage (0.04V - 0.7V) to fuel percentage (0-100%)
  - Supports all 4 ADC channels (default: channel 0)
  - Includes voltage reading method for debugging

### 2. main.py
- Updated imports: `IRSensor` and `FuelSensor` instead of `HallEffectSensor`
- Initialized fuel sensor in `DeadReckoningSystem.__init__()`
- Replaced `_read_fuel_level()` placeholder with actual fuel sensor reading
- Updated cleanup method to use `ir_sensor` instead of `hall_sensor`

### 3. config.py
- Changed `HALL_SENSOR_PIN` to `IR_SENSOR_PIN = 27`
- Removed `FUEL_SENSOR_PIN` (now uses ADC)
- Added fuel sensor ADC configuration:
  - `FUEL_ADC_CHANNEL = 0` (A0 on ADS1115)
  - `MIN_FUEL_VOLTAGE = 0.04` (empty tank)
  - `MAX_FUEL_VOLTAGE = 0.7` (full tank)

### 4. requirements.txt
- Removed: `RPi.GPIO`
- Added:
  - `gpiozero>=2.0.0` (for IR sensor)
  - `adafruit-circuitpython-ads1x15>=2.2.0` (for ADC)
  - `adafruit-blinka>=8.0.0` (CircuitPython compatibility)

### 5. New Files
- `test_sensors.py` - Sensor testing utility
  - Test IR sensor individually
  - Test fuel sensor individually
  - Test both sensors together
  
- `install.sh` - Automated installation script
  - Updates system packages
  - Enables I2C interface
  - Installs Python dependencies
  - Scans for I2C devices

- `README.md` - Complete documentation
- `CHANGES.md` - This file

## Pin Mapping

| Component | Connection | Pin/Address |
|-----------|-----------|-------------|
| IR Sensor | GPIO | 27 |
| AS5600 Steering | I2C | 0x36 |
| ADS1115 ADC | I2C | 0x48 (default) |
| Fuel Sensor | ADS1115 A0 | Channel 0 |

## Configuration Notes

### IR Sensor
- Detects wheel rotation pulses
- Counts pulses per second (RPS)
- Converts to RPM (RPS × 60)
- No pull-up resistor needed (sensor provides its own)

### Fuel Sensor
- Analog voltage output
- Connected to ADS1115 channel A0
- Voltage range: 0.04V (empty) to 0.7V (full)
- Inverted logic: higher voltage = more fuel
- Clamped to 0-100% range

### Dashboard
- Uses HTML/JavaScript instead of tkinter
- Accessible via web browser at port 5000
- Shows real-time map, lap count, and fuel level
- Updates at 2 Hz (sensor loop runs at 100 Hz)

## Testing

1. Test individual sensors:
```bash
python3 test_sensors.py
```

2. Verify I2C devices:
```bash
sudo i2cdetect -y 1
```
Should show:
- 0x36 (AS5600 steering encoder)
- 0x48 (ADS1115 ADC)

3. Run full system:
```bash
python3 main.py
```

## Python 3 Compatibility
- All code uses Python 3 syntax
- Shebang: `#!/usr/bin/env python3`
- Print statements use function syntax
- All imports compatible with Python 3.7+

## Dashboard Access
```
http://<raspberry-pi-ip>:5000
```

Replace `<raspberry-pi-ip>` with your Raspberry Pi's IP address.
