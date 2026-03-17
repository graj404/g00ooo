# Dead Reckoning Error Management

## The Problem: Error Accumulation

Dead reckoning accumulates errors over time because:

1. **Sensor Noise**: Small errors in steering angle and RPM readings
2. **Wheel Slip**: Wheels spin but vehicle doesn't move exactly as calculated
3. **Timing Variations**: Small variations in dt between updates
4. **Floating Point Rounding**: Tiny errors in calculations
5. **Heading Drift**: Small heading errors compound over distance

### Error Growth Without Reset:

```
Lap 1:  0.5m error   ✓ Acceptable
Lap 2:  1.2m error   ✓ Still okay
Lap 5:  3.5m error   ⚠️ Getting worse
Lap 10: 8.0m error   ❌ Bad
Lap 20: 18.0m error  ❌ Very bad
Lap 50: 50.0m error  ❌ Completely unusable!
```

**Why it grows:**
- Each lap's error adds to the next
- Small 1% error per lap = 50% error after 50 laps
- Position drifts further from reality

## The Solution: Lap-Based Reset

### Configuration

In `config.py`:
```python
ENABLE_LAP_RESET = True  # Reset position at each lap
```

### How It Works

When a lap completes:

1. **Measure Error**: Calculate distance from origin
   ```python
   error = √(x² + y²)
   ```

2. **Log Error**: Store for statistics
   ```python
   lap_errors.append(error)
   ```

3. **Reset Position**: Move back to origin
   ```python
   position = [0.0, 0.0]
   ```

4. **Keep Heading**: Don't reset heading (maintains continuity)

### Example Output

```
==================================================
LAP 3 COMPLETED - ERROR ANALYSIS
==================================================
Position error: 0.847 m
Average error per lap: 0.623 m
Cumulative error: 1.869 m
Error percentage: 0.85%
Resetting position to origin...
==================================================
```

## Error Statistics

At the end of your session:

```
==================================================
FINAL ERROR STATISTICS
==================================================
Total laps: 10
Average error per lap: 0.654 m
Maximum error: 1.234 m
Minimum error: 0.321 m
Cumulative error: 6.540 m

Error per lap: ['0.45m', '0.67m', '0.85m', '0.54m', '0.72m', 
                '0.61m', '0.89m', '0.43m', '1.23m', '0.65m']
==================================================
```

## Comparison: With vs Without Reset

### Without Reset (ENABLE_LAP_RESET = False)

| Lap | Position Error | Cumulative |
|-----|----------------|------------|
| 1 | 0.5m | 0.5m |
| 5 | 3.5m | 8.2m |
| 10 | 8.0m | 45.3m |
| 20 | 18.0m | 180.5m |
| 50 | 50.0m | 1250.0m |

**Result:** After 50 laps, you're 50+ meters off! ❌

### With Reset (ENABLE_LAP_RESET = True)

| Lap | Position Error | Cumulative |
|-----|----------------|------------|
| 1 | 0.5m | 0.5m |
| 5 | 0.6m | 2.8m |
| 10 | 0.7m | 6.2m |
| 20 | 0.6m | 12.4m |
| 50 | 0.7m | 31.5m |

**Result:** Each lap has ~0.5-0.7m error, but doesn't accumulate! ✅

## Why This Works

### Error Per Lap (Bounded)
```
Lap 1: Start at (0,0) → End at (0.5, 0.2) → Error: 0.54m
       Reset to (0,0)
       
Lap 2: Start at (0,0) → End at (0.6, 0.3) → Error: 0.67m
       Reset to (0,0)
       
Lap 3: Start at (0,0) → End at (0.4, 0.5) → Error: 0.64m
       Reset to (0,0)
```

**Each lap starts fresh!** Error doesn't compound.

### Cumulative Error (Tracking Only)
```
Cumulative = Sum of all lap errors
           = 0.54 + 0.67 + 0.64 + ...
           = Total drift over all laps
```

This is just for statistics, doesn't affect position.

## Typical Error Values

### Good System (Well-calibrated sensors):
- Error per lap: 0.3 - 0.8 m
- Error percentage: 0.3 - 0.8% of lap distance
- After 50 laps: Still usable ✓

### Poor System (Uncalibrated or noisy sensors):
- Error per lap: 1.5 - 3.0 m
- Error percentage: 1.5 - 3.0% of lap distance
- After 50 laps: Marginal ⚠️

### Broken System (Bad sensors or wrong config):
- Error per lap: 5.0+ m
- Error percentage: 5%+ of lap distance
- After 50 laps: Unusable ❌

## Error Sources and Mitigation

| Error Source | Impact | Mitigation |
|--------------|--------|------------|
| Wheel slip | High | Use on good traction surfaces |
| Sensor noise | Medium | Calibrate sensors properly |
| Timing jitter | Low | Use time.perf_counter() |
| Wheelbase error | Medium | Measure wheelbase accurately |
| Heading drift | High | Reset at each lap ✓ |

## When to Use Reset

### Use Reset (ENABLE_LAP_RESET = True) When:
✅ Racing on a closed track (laps)
✅ Need consistent accuracy over many laps
✅ Track has a clear start/finish line
✅ Lap distance > 50m

### Don't Use Reset (ENABLE_LAP_RESET = False) When:
❌ Point-to-point navigation (no laps)
❌ Open track without defined start
❌ Need absolute position tracking
❌ Using GPS or other absolute reference

## Advanced: Drift Correction

Future enhancement (not yet implemented):

```python
# Calculate drift rate
drift_per_meter = error / lap_distance

# Apply correction to future calculations
dx_corrected = dx * (1 - drift_per_meter)
dy_corrected = dy * (1 - drift_per_meter)
```

This would reduce error even further!

## Summary

**Problem:** Dead reckoning error grows unbounded
- 0.5m → 3.5m → 8m → 50m over 50 laps ❌

**Solution:** Reset position at each lap
- 0.5m → 0.6m → 0.7m → 0.6m over 50 laps ✅

**Result:** Usable for 50+ laps with consistent accuracy!

**Configuration:**
```python
ENABLE_LAP_RESET = True  # Keep this enabled for racing!
```
