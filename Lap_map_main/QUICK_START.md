# Quick Start - Hardware Testing Server

## 🚀 Start Server

**Windows:**
```bash
start_tester.bat
```

**Linux/Mac:**
```bash
./start_tester.sh
```

**Manual:**
```bash
python web_tester.py
```

## 🌐 Access Interfaces

| Interface | URL | Purpose |
|-----------|-----|---------|
| Main Dashboard | http://127.0.0.1:8888 | Full testing interface |
| 5" Display | http://127.0.0.1:8888/display | Hardware display simulator |

## 📋 Testing Workflow

1. **Open** → http://127.0.0.1:8888
2. **Select** → Click a test track (left panel)
3. **Start** → Click "▶ Start Test"
4. **Watch** → Monitor path and data
5. **Verify** → Check lap counting
6. **Stop/Reset** → Use control buttons

## 🏁 Test Tracks

| Track | Duration | Best For |
|-------|----------|----------|
| Circle | 60s | Basic verification |
| Oval | 80s | Lap counting |
| Figure-8 | 100s | Complex patterns |
| Slalom | 60s | Steering filter |
| High-Speed | 50s | Speed accuracy |

## 📊 What to Check

### ✅ Path Visualization
- Path plots correctly
- Current position marked (yellow pulsing circle)
- Heading shown (red line)
- Start point visible (green dot)

### ✅ Lap Counting
- Counts when returning to start
- Minimum 10m lap distance enforced
- Current lap resets after completion
- Total distance accumulates

### ✅ Sensor Data
- Velocity updates from RPM
- Steering angle changes smoothly
- No sudden jumps
- Values are reasonable

### ✅ Display Output
- 5" display section updates
- Shows: velocity, lap distance, total distance
- Large, readable numbers

## 🎯 Expected Results

| Track | Laps | Lap Distance | Error |
|-------|------|--------------|-------|
| Circle | 2-3 | ~157m | < 2m |
| Oval | 1-2 | ~200-250m | < 3m |
| Figure-8 | varies | varies | < 4m |

## ⚙️ Configuration

Fixed parameters (as requested):
- **dt = 0.2s** (update rate)
- **Start position**: (0, 0)
- **Initial heading**: 0 radians

From config.py:
- **Wheel circumference**: 0.628m
- **PI Filter**: Enabled (Kp=0.8, Ki=0.05)
- **Integration**: RK2 (more accurate)

## 🔧 Troubleshooting

### Server won't start
```bash
# Check port 8888
netstat -tuln | grep 8888
```

### Dashboard not loading
- Clear browser cache
- Check browser console
- Verify templates folder exists

### Path not updating
- Check WebSocket connection
- Verify test is running
- Try stop/start

### Lap not counting
- Path must return within 2m of (0,0)
- Minimum lap distance: 10m
- Check console for lap messages

## 📝 Next Steps

1. ✅ Test all 5 tracks
2. ✅ Verify lap counting works
3. ✅ Note typical error values
4. ✅ Check display output
5. ✅ Deploy to hardware (main.py)

## 🎓 Documentation

- **TESTING_GUIDE.md** - Complete usage guide
- **TESTER_SUMMARY.md** - Full system overview
- **README.md** - Hardware deployment guide

## 💡 Key Points

- Testing server uses **same algorithms** as hardware
- Successful tests = hardware will work
- No sensors needed for testing
- Safe to experiment and iterate
- After testing, deploy with confidence

---

**Ready to test!** Start the server and select a track.

Questions? Check TESTING_GUIDE.md for detailed information.

**Windows Users**: Server runs on http://127.0.0.1:8888
