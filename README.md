# Racing Lap Counter System

Dead reckoning navigation system for go-kart/racing vehicle with lap counting, path visualization, and web dashboard.

## Hardware Requirements

- Raspberry Pi 5 (8GB)
- IR Sensor (GPIO 27) - for wheel speed/RPM measurement
- AS5600 Magnetic Encoder (I2C) - for steering angle
- ADS1115 ADC (I2C) - for fuel level sensor
- Fuel level sensor (analog output)

## Pin Configuration

### IR Sensor
- GPIO Pin: 27
- Connection: Digital output from IR sensor to GPIO 27
- Pull-up: Disabled (sensor provides its own pull-up)

### Fuel Sensor (via ADS1115 ADC)
- ADC Channel: A0 (channel 0)
- Voltage Range: 0.04V (empty) to 0.7V (full)
- Connection: Analog output from fuel sensor to ADS1115 A0

### AS5600 Steering Encoder
- I2C Address: 0x36
- SDA: GPIO 2 (Pin 3)
- SCL: GPIO 3 (Pin 5)

## Installation

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Test sensors:
```bash
python3 test_sensors.py
```

3. Run the main system:
```bash
python3 main.py
```

## Configuration

Edit `config.py` to adjust:
- Sensor pins
- Wheel diameter and magnets per revolution
- Update rate (default: 100 Hz)
- Fuel voltage range
- Dashboard settings

## Web Dashboard

The system includes a web dashboard accessible at:
```
http://<raspberry-pi-ip>:5000
```

Features:
- Real-time path visualization
- Lap counter (top right)
- Fuel level indicator (bottom right)
- Auto-scaling map view

## Features

- Dead reckoning position tracking
- Lap counting with error correction
- Real-time RPM/RPS measurement
- Fuel level monitoring
- Web-based dashboard
- Path logging to CSV

## Files

- `main.py` - Main application
- `sensors.py` - IR sensor, fuel sensor, and steering encoder drivers
- `lap_counter.py` - Lap counting logic
- `web_dashboard.py` - Web dashboard server
- `config.py` - Configuration settings
- `test_sensors.py` - Sensor testing utility
- `pi_filter.py` - PI filter for sensor smoothing
- `visualize_path.py` - Path visualization tool

## Usage

1. Position vehicle at starting point
2. Run `python3 main.py`
3. Calibrate steering (follow prompts)
4. Open web dashboard in browser
5. Start driving!

## Notes

- All code is Python 3 compatible
- Uses HTML dashboard instead of tkinter
- IR sensor replaces Hall effect sensor
- Fuel level read from ADS1115 ADC
- System runs at 100 Hz for accurate position tracking
- Dashboard updates at 2 Hz to reduce CPU load
