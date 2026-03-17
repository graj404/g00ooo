# Dead Reckoning Formulas

## Core Dead Reckoning Equations

### 1. Velocity from RPM (Hall Effect Sensor)
```
velocity = (RPM / 60) * wheel_circumference

where:
  RPM = (pulse_count / magnets_per_revolution) * (60 / Δt)
  wheel_circumference = π * wheel_diameter
```

**Example:**
- 18 magnets, 54 pulses in 0.1s
- RPM = (54 / 18) * (60 / 0.1) = 1800 RPM
- If wheel diameter = 0.2m, circumference = 0.628m
- velocity = (1800 / 60) * 0.628 = 18.84 m/s

### 2. Linear Motion (Straight Line)
Used when |steering_angle| < 0.01 radians (~0.57°)

```
displacement = velocity × Δt
dx = displacement × cos(heading) = velocity × Δt × cos(heading)
dy = displacement × sin(heading) = velocity × Δt × sin(heading)

x(t+1) = x(t) + dx
y(t+1) = y(t) + dy
```

**IMPORTANT:** Position update is NOT `x(t+1) = x(t) + Δt` ❌  
**CORRECT:** `x(t+1) = x(t) + velocity × Δt × cos(heading)` ✅

**Example:**
- velocity = 5 m/s, Δt = 0.01s, heading = 45° (0.785 rad)
- displacement = 5 × 0.01 = 0.05m
- dx = 0.05 × cos(0.785) = 0.0354m
- dy = 0.05 × sin(0.785) = 0.0354m
- x(t+1) = x(t) + 0.0354
- y(t+1) = y(t) + 0.0354

**Why velocity matters:**
- At 1 m/s: moves 0.01m per update
- At 10 m/s: moves 0.10m per update
- At 100 m/s: moves 1.00m per update

### 3. Circular Arc Motion (Turning)
Used when |steering_angle| >= 0.01 radians

```
heading_rate = (velocity × tan(steering_angle)) / wheelbase
heading(t+1) = heading(t) + heading_rate × Δt
heading_normalized = atan2(sin(heading), cos(heading))

displacement = velocity × Δt
dx = displacement × cos(heading_normalized) = velocity × Δt × cos(heading)
dy = displacement × sin(heading_normalized) = velocity × Δt × sin(heading)

x(t+1) = x(t) + dx
y(t+1) = y(t) + dy
```

**Example:**
- velocity = 5 m/s, steering_angle = 15° (0.262 rad), wheelbase = 1m, Δt = 0.01s
- heading_rate = (5 × tan(0.262)) / 1 = 1.339 rad/s
- heading(t+1) = heading(t) + 1.339 × 0.01 = heading(t) + 0.0134 rad
- displacement = 5 × 0.01 = 0.05m
- dx = 0.05 × cos(heading(t+1))
- dy = 0.05 × sin(heading(t+1))
- x(t+1) = x(t) + dx
- y(t+1) = y(t) + dy

### 4. Heading Normalization
Keeps heading in range [-π, π]

```
heading_normalized = atan2(sin(heading), cos(heading))
```

### 5. Distance Calculation
Euclidean distance between two points

```
distance = √((x2 - x1)² + (y2 - y1)²)
```

Or using NumPy:
```python
distance = np.linalg.norm(position2 - position1)
```

## Lap Counting Logic

### 1. Distance from Start
```
distance_from_start = √((x - x_start)² + (y - y_start)²)
is_near_start = distance_from_start < start_threshold
```

### 2. Lap Completion Conditions
1. Vehicle was NOT near start (was_near_start = False)
2. Vehicle is NOW near start (is_near_start = True)
3. Vehicle left start zone (left_start_zone = True)
4. Current lap distance >= minimum lap distance (e.g., 10m)

### 3. Opposite Direction Detection
Uses dot product of approach vectors:

```
approach_vector = (position_current - position_10_steps_ago) / ||...||
dot_product = approach_vector_current · approach_vector_previous_lap

if dot_product < -0.5:
    # Opposite direction detected
```

**Interpretation:**
- dot_product = 1: Same direction
- dot_product = 0: Perpendicular
- dot_product = -1: Opposite direction

## Sensor Readings

### AS5600 Magnetic Encoder (Steering Angle)
```
raw_value = (high_byte << 8) | low_byte  # 12-bit value (0-4095)
angle_radians = (raw_value / 4096) * 2π - zero_offset

# Normalize to [-π, π]
while angle_radians > π:
    angle_radians -= 2π
while angle_radians < -π:
    angle_radians += 2π
```

### AS314 Hall Effect Sensor (RPM)
```
RPM = (pulse_count / magnets_per_revolution) * (60 / Δt)

where:
  pulse_count = number of magnet detections in time period Δt
  magnets_per_revolution = 18 (for 20° spacing)
  Δt = time period in seconds
```

## Performance Optimization

### NumPy Acceleration
All calculations use NumPy arrays for C-level performance:

```python
# Position update (vectorized)
self.position += np.array([dx, dy], dtype=np.float64)

# Trigonometric functions (optimized)
np.cos(heading)
np.sin(heading)
np.tan(steering_angle)
np.arctan2(y, x)

# Distance calculation (optimized)
np.linalg.norm(vector)
```

### Update Rate
- Target: 100 Hz (10ms per update)
- Actual Δt measured using `time.perf_counter()`
- Ensures accurate distance calculations regardless of timing variations

## Coordinate System

```
        Y (North)
        ^
        |
        |
        +-------> X (East)
      (0,0)

Heading:
  0° = East (+X direction)
  90° = North (+Y direction)
  180° = West (-X direction)
  270° = South (-Y direction)
```

## Error Sources & Mitigation

1. **Wheel Slip**: Dead reckoning assumes no wheel slip
   - Mitigation: Use on surfaces with good traction

2. **Sensor Noise**: Hall sensor pulse counting can be noisy
   - Mitigation: 100ms minimum update period for RPM

3. **Heading Drift**: Small errors accumulate over time
   - Mitigation: Lap completion resets relative position

4. **Wheelbase Approximation**: Simplified Ackermann model
   - Mitigation: Calibrate wheelbase parameter to match vehicle
