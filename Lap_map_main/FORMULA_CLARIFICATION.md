# Formula Clarification - Position Update

## ❌ WRONG Formula

```
x(t+1) = x(t) + Δt
```

This is **INCORRECT** because:
- Doesn't account for velocity (speed)
- Doesn't account for direction (heading)
- Would move same distance whether going 1 m/s or 100 m/s
- Units don't match: x is in meters, Δt is in seconds

## ✅ CORRECT Formula

```
x(t+1) = x(t) + velocity × Δt × cos(heading)
y(t+1) = y(t) + velocity × Δt × sin(heading)
```

Or broken down:
```
dx = velocity × Δt × cos(heading)
dy = velocity × Δt × sin(heading)
x(t+1) = x(t) + dx
y(t+1) = y(t) + dy
```

## Why This Makes Sense

### Physics Basis
```
distance = velocity × time
```

In 2D with direction:
```
displacement_x = distance × cos(heading)
displacement_y = distance × sin(heading)
```

Combined:
```
displacement_x = velocity × Δt × cos(heading)
displacement_y = velocity × Δt × sin(heading)
```

### Unit Analysis

**Wrong formula:**
```
x(t+1) = x(t) + Δt
[meters] = [meters] + [seconds]  ❌ Units don't match!
```

**Correct formula:**
```
x(t+1) = x(t) + velocity × Δt × cos(heading)
[meters] = [meters] + [m/s] × [s] × [dimensionless]
[meters] = [meters] + [meters]  ✅ Units match!
```

## Complete Example

### Given:
- Current position: x(t) = 10 m, y(t) = 5 m
- Velocity: 5 m/s
- Heading: 45° = 0.785 rad
- Time step: Δt = 0.01 s

### Calculate:

**Step 1:** Calculate displacement components
```
dx = velocity × Δt × cos(heading)
dx = 5 × 0.01 × cos(0.785)
dx = 0.05 × 0.707
dx = 0.0354 m

dy = velocity × Δt × sin(heading)
dy = 5 × 0.01 × sin(0.785)
dy = 0.05 × 0.707
dy = 0.0354 m
```

**Step 2:** Update position
```
x(t+1) = x(t) + dx
x(t+1) = 10 + 0.0354
x(t+1) = 10.0354 m

y(t+1) = y(t) + dy
y(t+1) = 5 + 0.0354
y(t+1) = 5.0354 m
```

**Result:** Vehicle moved from (10, 5) to (10.0354, 5.0354) in 0.01 seconds

### Verification:
```
distance_traveled = √(dx² + dy²)
distance_traveled = √(0.0354² + 0.0354²)
distance_traveled = √(0.00125 + 0.00125)
distance_traveled = √0.0025
distance_traveled = 0.05 m

Check: velocity × Δt = 5 × 0.01 = 0.05 m ✅
```

## Different Velocities Comparison

At heading = 0° (East), Δt = 0.01s:

| Velocity | dx | dy | New Position |
|----------|----|----|--------------|
| 1 m/s | 0.01 m | 0 m | (10.01, 5.00) |
| 5 m/s | 0.05 m | 0 m | (10.05, 5.00) |
| 10 m/s | 0.10 m | 0 m | (10.10, 5.00) |
| 100 m/s | 1.00 m | 0 m | (11.00, 5.00) |

**Notice:** Faster velocity = larger position change (as expected!)

With wrong formula `x(t+1) = x(t) + Δt`:
- All velocities would give: (10.01, 5.00) ❌ Wrong!

## Summary

### Complete Dead Reckoning Update:

```python
# 1. Get velocity from sensors
velocity = (RPM / 60) × wheel_circumference

# 2. Update heading (if turning)
if abs(steering_angle) >= 0.01:
    heading_rate = (velocity × tan(steering_angle)) / wheelbase
    heading = heading + heading_rate × Δt
    heading = atan2(sin(heading), cos(heading))  # Normalize

# 3. Calculate displacement
dx = velocity × Δt × cos(heading)
dy = velocity × Δt × sin(heading)

# 4. Update position
x = x + dx
y = y + dy
```

### Key Takeaway:

**Position change depends on:**
1. ✅ Velocity (how fast)
2. ✅ Time (how long)
3. ✅ Direction (which way)

**NOT just time alone!**
