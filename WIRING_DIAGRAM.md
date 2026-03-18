# Wiring Diagram - Racing Lap Counter System

## Raspberry Pi 5 GPIO Pinout Reference

```
     3V3  (1) (2)  5V
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

---

## 1. AS5600 Magnetic Angle Sensor (Steering)

**AS5600 Specifications:**
- I2C Address: 0x36
- Operating Voltage: 3.3V or 5V
- Resolution: 12-bit (4096 positions)
- Angle Range: 0-360 degrees

**Wiring:**

```
AS5600 Pin    →    Raspberry Pi Pin
─────────────────────────────────────
VCC (3.3V)    →    Pin 1  (3.3V)
GND           →    Pin 6  (GND)
SDA           →    Pin 3  (GPIO2 - SDA)
SCL           →    Pin 5  (GPIO3 - SCL)
DIR           →    Not connected (optional)
```

**Visual Diagram:**

```
┌─────────────────┐
│   AS5600        │
│  Angle Sensor   │
├─────────────────┤
│ VCC  → Pin 1    │ (3.3V)
│ GND  → Pin 6    │ (Ground)
│ SDA  → Pin 3    │ (GPIO2)
│ SCL  → Pin 5    │ (GPIO3)
│ DIR  → NC       │ (Not Connected)
└─────────────────┘
```

**Magnet Placement:**
- Place a diametric magnet on the steering shaft
- Distance: 0.5mm - 3mm from sensor surface
- Magnet should rotate with steering wheel
- Sensor remains stationary

---

## 2. IR Sensor (Wheel Speed/RPM)

**IR Sensor Specifications:**
- Operating Voltage: 3.3V - 5V
- Output: Digital (HIGH/LOW)
- Detection Range: 2-30cm (adjustable)

**Wiring:**

```
IR Sensor Pin    →    Raspberry Pi Pin
─────────────────────────────────────
VCC (+)          →    Pin 2  (5V)
GND (-)          →    Pin 9  (GND)
OUT (Signal)     →    Pin 13 (GPIO27)
```

**Visual Diagram:**

```
┌─────────────────┐
│   IR Sensor     │
│  (Speed/RPM)    │
├─────────────────┤
│ VCC  → Pin 2    │ (5V)
│ GND  → Pin 9    │ (Ground)
│ OUT  → Pin 13   │ (GPIO27)
└─────────────────┘
```

**Wheel Mounting:**
- Attach reflective tape or disc to wheel
- Position IR sensor 2-5cm from wheel
- Sensor detects each rotation
- Adjust sensitivity potentiometer if needed

---

## 3. ADS1115 ADC (Analog to Digital Converter)

**ADS1115 Specifications:**
- I2C Address: 0x48 (default)
- Operating Voltage: 2.0V - 5.5V
- Resolution: 16-bit
- Channels: 4 (A0, A1, A2, A3)

**Wiring:**

```
ADS1115 Pin    →    Raspberry Pi Pin
─────────────────────────────────────
VDD           →    Pin 1  (3.3V)
GND           →    Pin 14 (GND)
SDA           →    Pin 3  (GPIO2 - SDA)
SCL           →    Pin 5  (GPIO3 - SCL)
ADDR          →    GND (for address 0x48)
ALRT          →    Not connected
A0            →    Fuel Sensor Signal
A1            →    Available
A2            →    Available
A3            →    Available
```

**Visual Diagram:**

```
┌─────────────────┐
│   ADS1115 ADC   │
├─────────────────┤
│ VDD  → Pin 1    │ (3.3V)
│ GND  → Pin 14   │ (Ground)
│ SDA  → Pin 3    │ (GPIO2)
│ SCL  → Pin 5    │ (GPIO3)
│ ADDR → GND      │
│ A0   → Fuel     │ (Fuel Sensor)
│ A1   → NC       │
│ A2   → NC       │
│ A3   → NC       │
└─────────────────┘
```

---

## 4. Fuel Level Sensor (Analog)

**Fuel Sensor Specifications:**
- Output: Analog voltage (0.04V - 0.7V)
- Type: Resistive or capacitive
- Operating Voltage: 5V or 12V (depends on sensor)

**Wiring:**

```
Fuel Sensor Pin    →    Connection
─────────────────────────────────────
VCC (+)            →    5V or 12V (external power)
GND (-)            →    Common Ground
Signal (OUT)       →    ADS1115 A0
```

**Visual Diagram:**

```
┌─────────────────┐
│  Fuel Sensor    │
├─────────────────┤
│ VCC  → 5V/12V   │ (External Power)
│ GND  → GND      │ (Common Ground)
│ OUT  → ADS A0   │ (To ADS1115 channel A0)
└─────────────────┘
```

**Voltage Range:**
- Empty Tank: 0.04V
- Full Tank: 0.7V
- Adjust in `config.py` if different

---

## Complete System Wiring Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 5                             │
│                                                               │
│  Pin 1  (3.3V)  ──┬─→ AS5600 VCC                            │
│                   └─→ ADS1115 VDD                            │
│                                                               │
│  Pin 2  (5V)    ────→ IR Sensor VCC                          │
│                                                               │
│  Pin 3  (GPIO2) ──┬─→ AS5600 SDA                            │
│         SDA       └─→ ADS1115 SDA                            │
│                                                               │
│  Pin 5  (GPIO3) ──┬─→ AS5600 SCL                            │
│         SCL       └─→ ADS1115 SCL                            │
│                                                               │
│  Pin 6  (GND)   ────→ AS5600 GND                             │
│  Pin 9  (GND)   ────→ IR Sensor GND                          │
│  Pin 14 (GND)   ──┬─→ ADS1115 GND                            │
│                   └─→ Common Ground                          │
│                                                               │
│  Pin 13 (GPIO27)────→ IR Sensor OUT                          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
         ↓                    ↓                    ↓
    ┌─────────┐         ┌─────────┐         ┌──────────┐
    │ AS5600  │         │IR Sensor│         │ ADS1115  │
    │ Steering│         │  Speed  │         │   ADC    │
    └─────────┘         └─────────┘         └────┬─────┘
                                                  │
                                                  ↓ A0
                                            ┌──────────┐
                                            │   Fuel   │
                                            │  Sensor  │
                                            └──────────┘
```

---

## I2C Device Addresses

After wiring, verify I2C devices are detected:

```bash
sudo i2cdetect -y 1
```

**Expected Output:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- 36 -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

- `36` = AS5600 Steering Angle Sensor
- `48` = ADS1115 ADC

---

## Power Requirements

| Component | Voltage | Current | Power Source |
|-----------|---------|---------|--------------|
| Raspberry Pi 5 | 5V | 3A | USB-C Power Supply |
| AS5600 | 3.3V | 6.5mA | Pi Pin 1 |
| IR Sensor | 5V | 20mA | Pi Pin 2 |
| ADS1115 | 3.3V | 150μA | Pi Pin 1 |
| Fuel Sensor | 5-12V | Varies | External Power |

**Total Pi GPIO Current:** ~30mA (well within limits)

---

## Configuration in Code

Edit `config.py` to match your wiring:

```python
# Sensor Pins
IR_SENSOR_PIN = 27              # GPIO27 (Pin 13)
AS5600_I2C_ADDRESS = 0x36       # I2C address
FUEL_ADC_CHANNEL = 0            # ADS1115 channel A0

# Fuel Sensor Voltage Range
MIN_FUEL_VOLTAGE = 0.04         # Empty tank
MAX_FUEL_VOLTAGE = 0.7          # Full tank
```

---

## Testing Connections

**1. Test I2C devices:**
```bash
sudo i2cdetect -y 1
```

**2. Test individual sensors:**
```bash
python3 test_sensors.py
```

**3. Run full system:**
```bash
python3 main.py
```

---

## Troubleshooting

**AS5600 not detected (no 0x36):**
- Check SDA/SCL connections
- Verify 3.3V power
- Enable I2C: `sudo raspi-config` → Interface → I2C

**ADS1115 not detected (no 0x48):**
- Check I2C wiring
- Verify ADDR pin is connected to GND
- Check 3.3V power

**IR Sensor not working:**
- Check GPIO27 connection
- Verify 5V power
- Adjust sensitivity potentiometer
- Test with multimeter (should toggle between 0V and 5V)

**Fuel reading always 0% or 100%:**
- Check ADS1115 A0 connection
- Verify fuel sensor power
- Adjust MIN_FUEL_VOLTAGE and MAX_FUEL_VOLTAGE in config.py
- Test voltage with multimeter

---

## Safety Notes

⚠️ **Important:**
- Never connect 5V directly to 3.3V pins
- Use common ground for all components
- Double-check polarity before powering on
- Use proper gauge wire for current requirements
- Secure all connections to prevent shorts
- Keep sensors away from heat sources

---

## Additional Resources

- [AS5600 Datasheet](https://ams.com/as5600)
- [ADS1115 Datasheet](https://www.ti.com/product/ADS1115)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz)
- [I2C Configuration Guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
