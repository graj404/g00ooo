# Interface Guide - Visual Walkthrough

## Main Testing Dashboard

### Layout Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│  🏎️ Dead Reckoning Hardware Tester          ● Ready                │
├──────────────┬──────────────────────────────┬───────────────────────┤
│              │                              │                       │
│  📋 Test     │   🗺️ 2D Path               │  📊 Data Panel        │
│  Tracks      │   Visualization              │                       │
│              │                              │  📍 Position Data     │
│  ┌────────┐ │   ┌────────────────────┐    │  X: 12.34 m          │
│  │ Circle │ │   │                    │    │  Y: 5.67 m           │
│  └────────┘ │   │    [Live Path      │    │  Heading: 45.0°      │
│              │   │     Plotting]      │    │                       │
│  ┌────────┐ │   │                    │    │  🏁 Lap Information  │
│  │  Oval  │ │   │    Yellow dot =    │    │  Lap Count: 2        │
│  └────────┘ │   │    Current pos     │    │  Current Lap: 127.5m │
│              │   │                    │    │  Total: 384.2m       │
│  ┌────────┐ │   │    Red line =      │    │                       │
│  │Figure-8│ │   │    Heading         │    │  🔧 Sensor Inputs    │
│  └────────┘ │   │                    │    │  Velocity: 15.3 m/s  │
│              │   │    Green dot =     │    │  RPM: 300           │
│  ┌────────┐ │   │    Start (0,0)     │    │  Steering: 15.0°    │
│  │ Slalom │ │   │                    │    │                       │
│  └────────┘ │   └────────────────────┘    │  📺 5" Display       │
│              │                              │  ┌─────────────────┐ │
│  ┌────────┐ │                              │  │ VELOCITY        │ │
│  │ Speed  │ │                              │  │ 15.3 m/s        │ │
│  └────────┘ │                              │  ├─────────────────┤ │
│              │                              │  │ CURRENT LAP     │ │
│  ▶ Start    │                              │  │ 127.5 m         │ │
│  ⏹ Stop     │                              │  ├─────────────────┤ │
│  🔄 Reset    │                              │  │ TOTAL DISTANCE  │ │
│              │                              │  │ 384.2 m         │ │
│              │                              │  └─────────────────┘ │
└──────────────┴──────────────────────────────┴───────────────────────┘
```

## Color Scheme

### Main Dashboard
- **Background**: Blue gradient (professional)
- **Panels**: Dark translucent (modern)
- **Accent**: Green (#4CAF50)
- **Text**: White
- **Status**: Green (ready), Orange (stopped), Red (error)

### Path Visualization
- **Background**: Black
- **Grid**: Light green (10% opacity)
- **Axes**: Green (30% opacity)
- **Path**: Bright green (#00ff00)
- **Start Point**: Green circle
- **Current Position**: Yellow pulsing circle
- **Heading**: Red line

### 5" Display Simulator
- **Background**: Black
- **Text**: Green (#0f0)
- **Borders**: Green
- **Style**: Terminal/retro

## Interactive Elements

### Track Selection
```
┌────────────────────────────┐
│ Circle Track               │  ← Click to select
│ Simple circular path       │
│ 50m diameter               │
└────────────────────────────┘
     ↓ (when selected)
┌────────────────────────────┐
│ Circle Track               │  ← Highlighted in green
│ Simple circular path       │     with glow effect
│ 50m diameter               │
└────────────────────────────┘
```

### Control Buttons
```
┌──────────────┐
│ ▶ Start Test │  ← Green button, enabled when track selected
└──────────────┘

┌──────────────┐
│ ⏹ Stop Test  │  ← Red button, enabled when running
└──────────────┘

┌──────────────┐
│ 🔄 Reset     │  ← Orange button, always enabled
└──────────────┘
```

### Status Indicator
```
● Ready        ← Green pulsing dot
● Running      ← Green solid dot
● Stopped      ← Orange dot
● Error        ← Red dot
```

## Path Visualization Details

### Elements on Canvas
```
        Y
        ↑
        │
    ┌───┼───┐
    │   │   │
────┼───●───┼──── X     ● = Start point (0,0) - Green
    │   │   │
    └───┼───┘
        │
        
Path:  ─────────────────      Green line, 3px width

Current Position:  ◉           Yellow circle, pulsing
                               Size: 15-25px (animated)

Heading:  ◉───→               Red line from position
                               Length: 30px

Grid:  ┼ ┼ ┼ ┼ ┼              Light green, 10m spacing
       ┼ ┼ ┼ ┼ ┼
```

### Auto-Scaling
- Automatically adjusts to fit entire path
- Maintains aspect ratio
- 50px padding on all sides
- Maximum scale: 20 pixels per meter
- Minimum scale: fits entire path

### Animation
- Current position pulses (50ms interval)
- Smooth path drawing
- Real-time updates (10 Hz)
- No flickering

## Data Display Format

### Position Data
```
┌─────────────────────────────┐
│ X Position:      12.34 m    │  ← 2 decimal places
│ Y Position:       5.67 m    │
│ Heading:         45.0°      │  ← 1 decimal place
└─────────────────────────────┘
```

### Lap Information
```
┌─────────────────────────────┐
│ Lap Count:            2     │  ← Integer
│ Current Lap:     127.50 m   │  ← 2 decimal places
│ Total Distance:  384.20 m   │
└─────────────────────────────┘
```

### Sensor Inputs
```
┌─────────────────────────────┐
│ Velocity:       15.30 m/s   │  ← 2 decimal places
│ RPM (AS314):         300    │  ← Integer
│ Steering (AS5600): 15.0°    │  ← 1 decimal place
└─────────────────────────────┘
```

## 5" Display Simulator

### Full Screen View
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │              VELOCITY                         │    │
│  │                                               │    │
│  │                15.3                           │    │  ← 72px font
│  │                                               │    │
│  │               m/s                             │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │        CURRENT LAP DISTANCE                   │    │
│  │                                               │    │
│  │               127.5                           │    │  ← 72px font
│  │                                               │    │
│  │              meters                           │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │          TOTAL DISTANCE                       │    │
│  │                                               │    │
│  │               384.2                           │    │  ← 72px font
│  │                                               │    │
│  │              meters                           │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
     800px × 480px (5" display resolution)
```

### Display Characteristics
- **Font**: Courier New (monospace)
- **Background**: Pure black (#000)
- **Text**: Bright green (#0f0)
- **Borders**: 3px solid green
- **Glow**: Text shadow effect
- **Update**: 10 Hz (100ms)
- **Values**: 1 decimal place

## Responsive Behavior

### Window Resize
- Canvas automatically resizes
- Maintains aspect ratio
- Path rescales to fit
- No distortion

### WebSocket Reconnect
- Automatic reconnection on disconnect
- Status indicator shows connection state
- No data loss
- Seamless recovery

## User Feedback

### Visual Feedback
```
Button Click:
  Normal:  [Button]
  Hover:   [Button]  ← Slightly larger, shadow
  Click:   [Button]  ← Scale animation
  
Track Selection:
  Normal:  [Track]
  Hover:   [Track]   ← Slide right 5px
  Active:  [Track]   ← Green background, glow
  
Status Changes:
  Ready → Running:   Green pulse → Solid green
  Running → Stopped: Solid green → Orange
  Stopped → Ready:   Orange → Green pulse
```

### Console Messages
```
Starting test: Circle Track
Lap 1 completed! Distance: 157.23m
Test stopped by user
System reset
```

## Accessibility

### Keyboard Navigation
- Tab: Navigate between controls
- Enter: Activate button
- Arrow keys: Select track
- Escape: Stop test

### Screen Reader Support
- All buttons labeled
- Status announcements
- Data updates announced
- Track descriptions read

## Performance Indicators

### Smooth Operation
- Path drawing: 60 FPS
- Data updates: 10 Hz
- No lag or stutter
- Responsive controls

### Loading States
```
Connecting...     ← WebSocket connecting
Loading tracks... ← Fetching track list
Starting test...  ← Initializing simulation
Running...        ← Active test
```

## Mobile View (Bonus)

While optimized for desktop, the interface adapts:
```
┌─────────────────┐
│  Header         │
├─────────────────┤
│  Track List     │
├─────────────────┤
│  Map (smaller)  │
├─────────────────┤
│  Data (compact) │
├─────────────────┤
│  Controls       │
└─────────────────┘
```

## Tips for Best Experience

### Recommended Setup
- **Browser**: Chrome, Firefox, or Edge (latest)
- **Screen**: 1920×1080 or larger
- **Connection**: Local (no network lag)
- **CPU**: Modern processor (smooth animations)

### Optimal Viewing
- Full screen mode (F11)
- Zoom: 100%
- Dark room (better contrast)
- Multiple monitors (dashboard + 5" display)

### Testing Tips
- Start with Circle track (simplest)
- Watch path develop completely
- Check lap counting accuracy
- Compare data panel with 5" display
- Try all tracks before hardware deployment

## Summary

The interface provides:
- ✅ Professional, modern design
- ✅ Clear visual hierarchy
- ✅ Real-time updates
- ✅ Smooth animations
- ✅ Intuitive controls
- ✅ Comprehensive data display
- ✅ Hardware display simulation
- ✅ Responsive behavior

**Access it**: http://localhost:8000 after running `python web_tester.py`
