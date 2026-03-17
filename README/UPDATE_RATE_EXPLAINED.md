# Update Rate Explained

## What Does 100 Hz Mean?

**100 Hz = 100 updates per second**

NOT "1 meter per second at 100 m/s" ❌

## The Math

### Formula:
```
distance_per_update = velocity × Δt

where:
  Δt = 1 / update_rate_Hz
```

### At 100 Hz (Δt = 0.01 seconds):

| Velocity | Distance per Update | Distance per Second |
|----------|---------------------|---------------------|
| 1 m/s | 0.01 m (1 cm) | 1 m (100 updates) |
| 10 m/s | 0.10 m (10 cm) | 10 m (100 updates) |
| 20 m/s | 0.20 m (20 cm) | 20 m (100 updates) |
| 50 m/s | 0.50 m (50 cm) | 50 m (100 updates) |
| 100 m/s | 1.00 m (100 cm) | 100 m (100 updates) |

### At 1000 Hz (Δt = 0.001 seconds):

| Velocity | Distance per Update | Distance per Second |
|----------|---------------------|---------------------|
| 1 m/s | 0.001 m (1 mm) | 1 m (1000 updates) |
| 10 m/s | 0.010 m (1 cm) | 10 m (1000 updates) |
| 20 m/s | 0.020 m (2 cm) | 20 m (1000 updates) |
| 50 m/s | 0.050 m (5 cm) | 50 m (1000 updates) |
| 100 m/s | 0.100 m (10 cm) | 100 m (1000 updates) |

## Example: 1 Second of Travel at 20 m/s

### With 100 Hz:
```
Time: 0.00s → Position: (0.00, 0.00)
Time: 0.01s → Position: (0.20, 0.00)  ← Update 1
Time: 0.02s → Position: (0.40, 0.00)  ← Update 2
Time: 0.03s → Position: (0.60, 0.00)  ← Update 3
...
Time: 0.99s → Position: (19.80, 0.00) ← Update 99
Time: 1.00s → Position: (20.00, 0.00) ← Update 100

Total: 100 updates, 20 meters traveled ✓
```

### With 1000 Hz:
```
Time: 0.000s → Position: (0.000, 0.00)
Time: 0.001s → Position: (0.020, 0.00)  ← Update 1
Time: 0.002s → Position: (0.040, 0.00)  ← Update 2
Time: 0.003s → Position: (0.060, 0.00)  ← Update 3
...
Time: 0.999s → Position: (19.980, 0.00) ← Update 999
Time: 1.000s → Position: (20.000, 0.00) ← Update 1000

Total: 1000 updates, 20 meters traveled ✓
```

**Same distance, but 10x more calculations!**

## Go-Kart Speed Analysis

### Typical Go-Kart Speeds:
- **Recreational**: 10-15 m/s (36-54 km/h)
- **Racing**: 20-30 m/s (72-108 km/h)
- **Professional**: 30-40 m/s (108-144 km/h)

### Accuracy at Different Update Rates:

**At 20 m/s (typical racing speed):**

| Update Rate | Δt | Distance/Update | Accuracy |
|-------------|-----|-----------------|----------|
| 10 Hz | 0.1 s | 2.0 m | Poor ❌ |
| 50 Hz | 0.02 s | 0.4 m | Okay ⚠️ |
| 100 Hz | 0.01 s | 0.2 m | Good ✅ |
| 200 Hz | 0.005 s | 0.1 m | Better ✅ |
| 1000 Hz | 0.001 s | 0.02 m | Overkill 🔥 |

**At 30 m/s (professional racing):**

| Update Rate | Δt | Distance/Update | Accuracy |
|-------------|-----|-----------------|----------|
| 10 Hz | 0.1 s | 3.0 m | Poor ❌ |
| 50 Hz | 0.02 s | 0.6 m | Okay ⚠️ |
| 100 Hz | 0.01 s | 0.3 m | Good ✅ |
| 200 Hz | 0.005 s | 0.15 m | Better ✅ |
| 1000 Hz | 0.001 s | 0.03 m | Overkill 🔥 |

## Sensor Limitations

### Hall Effect Sensor (AS314):
- **Magnet spacing**: 20° = 18 magnets
- **Wheel circumference**: ~0.628 m
- **Distance per magnet**: 0.628 / 18 = 0.035 m (3.5 cm)

**Sensor resolution: 3.5 cm**

**Conclusion:** Update rate faster than 100 Hz doesn't help much because sensor itself has 3.5cm resolution!

### AS5600 Steering Angle:
- **Resolution**: 12-bit = 4096 positions
- **Angle resolution**: 360° / 4096 = 0.088° (0.0015 rad)

**Very precise, 100 Hz is fine.**

## CPU Usage Comparison

| Update Rate | CPU Usage | Benefit |
|-------------|-----------|---------|
| 10 Hz | ~1% | Too slow ❌ |
| 50 Hz | ~3% | Okay ⚠️ |
| 100 Hz | ~5% | Perfect ✅ |
| 200 Hz | ~10% | Good if needed ✅ |
| 500 Hz | ~20% | Diminishing returns ⚠️ |
| 1000 Hz | ~30% | Wasteful ❌ |

## Recommendation by Use Case

### Recreational Go-Kart (10-15 m/s):
```python
UPDATE_RATE_HZ = 50  # 0.02s, 20-30cm per update
```
**Good enough, saves CPU**

### Racing Go-Kart (20-30 m/s):
```python
UPDATE_RATE_HZ = 100  # 0.01s, 20-30cm per update
```
**Recommended - best balance ✅**

### Professional Racing (30-40 m/s):
```python
UPDATE_RATE_HZ = 200  # 0.005s, 15-20cm per update
```
**Better accuracy if needed**

### High-Speed Testing (>50 m/s):
```python
UPDATE_RATE_HZ = 500  # 0.002s, 10cm per update
```
**Only if you really need it**

## Your Confusion Clarified

### ❌ Wrong Understanding:
> "100 Hz means at 100 m/s, 1 meter is updated per second"

**This would mean:**
- 1 update per second
- That's 1 Hz, not 100 Hz!

### ✅ Correct Understanding:
> "100 Hz means 100 updates per second"

**At 100 m/s:**
- 100 updates per second
- Each update: 100 m/s × 0.01s = 1 meter
- Total per second: 1m × 100 = 100 meters ✓

## Visual Timeline

### 100 Hz (10ms between updates):
```
0ms    10ms   20ms   30ms   40ms   50ms   60ms   70ms   80ms   90ms   100ms
|------|------|------|------|------|------|------|------|------|------|
  ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓
  U1     U2     U3     U4     U5     U6     U7     U8     U9     U10    U11

At 20 m/s: Each update moves 0.2m
After 100ms: 10 updates × 0.2m = 2m total ✓
```

### 1000 Hz (1ms between updates):
```
0ms 1ms 2ms 3ms 4ms 5ms 6ms 7ms 8ms 9ms 10ms
|---|---|---|---|---|---|---|---|---|---|---|
 ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓   ↓
 U1  U2  U3  U4  U5  U6  U7  U8  U9  U10 U11

At 20 m/s: Each update moves 0.02m
After 10ms: 10 updates × 0.02m = 0.2m total ✓
```

**Same distance, but 1000 Hz does 10x more work!**

## Final Answer

**For your go-kart:**
```python
UPDATE_RATE_HZ = 100  # Keep this! ✅
```

**Why:**
- ✅ 20-30cm accuracy at racing speed (perfect for lap tracking)
- ✅ Low CPU usage (~5%)
- ✅ Matches sensor resolution (3.5cm per magnet)
- ✅ Real-time dashboard works smoothly
- ✅ Proven in racing applications

**Don't use 1000 Hz unless:**
- You're going >100 m/s (you're not)
- You need millimeter accuracy (you don't)
- You have perfect sensors (you don't)

**100 Hz is the sweet spot! 🎯**
