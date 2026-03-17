#!/usr/bin/env python3
"""
Hardware Testing Server for Dead Reckoning System
Tests AS5600 (steering) and AS314 (RPM) sensors with simulated inputs
Professional web interface for verification before hardware deployment
"""

import time
import numpy as np
import threading
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from collections import deque

from lap_counter import LapCounter
from pi_filter import PISteeringObserver, PIVelocityObserver
from config import (
    WHEEL_CIRCUMFERENCE_M, INITIAL_X, INITIAL_Y, INITIAL_HEADING,
    ENABLE_PI_FILTER, PI_KP, PI_KI, MAX_STEERING_RATE_DEG_S,
    USE_RK2_INTEGRATION
)

app = FastAPI()

# Global state
test_state = {
    'x': 0.0,
    'y': 0.0,
    'heading': 0.0,
    'velocity': 0.0,
    'steering_angle': 0.0,
    'rpm': 0.0,
    'laps_completed': 0,
    'current_lap_distance': 0.0,
    'total_distance': 0.0,
    'reference_lap_distance': 0.0,
    'path_points': [],
    'running': False,
    'selected_track': 'circle'
}
state_lock = threading.Lock()
connected_clients = []


class TestingSystem:
    """Dead reckoning system for testing with simulated sensor inputs"""
    
    def __init__(self):
        self.position = np.array([INITIAL_X, INITIAL_Y], dtype=np.float64)
        self.heading = INITIAL_HEADING
        self.velocity = 0.0
        self.steering_angle = 0.0
        self.rpm = 0.0
        
        self.lap_counter = LapCounter(start_threshold=2.0, min_lap_distance=10.0)
        
        if ENABLE_PI_FILTER:
            self.pi_steering = PISteeringObserver(
                kp=PI_KP, ki=PI_KI, max_steering_rate_deg_s=MAX_STEERING_RATE_DEG_S
            )
        
        self.dt = 0.2  # Fixed dt = 0.2s as requested
        self.last_update = time.perf_counter()
        
    def update(self, steering_input, rpm_input):
        """Update system with simulated sensor inputs"""
        current_time = time.perf_counter()
        dt = self.dt  # Use fixed dt
        self.last_update = current_time
        
        # Simulate sensor readings
        self.rpm = rpm_input
        raw_steering = steering_input
        
        # Apply PI filter
        if ENABLE_PI_FILTER:
            self.steering_angle = self.pi_steering.update(raw_steering, dt)
        else:
            self.steering_angle = raw_steering
        
        # Calculate velocity from RPM
        self.velocity = (self.rpm / 60.0) * WHEEL_CIRCUMFERENCE_M
        
        # Dead reckoning
        if USE_RK2_INTEGRATION:
            self._update_position_rk2(dt)
        else:
            self._update_position_euler(dt)
        
        # Update lap counter
        laps, lap_dist, total_dist, lap_completed = self.lap_counter.update(self.position)
        
        return self.position, self.heading, self.velocity, laps, lap_dist, total_dist
    
    def _update_position_euler(self, dt):
        """Euler integration"""
        if abs(self.steering_angle) < 0.01:
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            heading_rate = self.velocity * np.tan(self.steering_angle) / 1.0
            self.heading += heading_rate * dt
            self.heading = np.arctan2(np.sin(self.heading), np.cos(self.heading))
            
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
    
    def _update_position_rk2(self, dt):
        """RK2 integration"""
        if abs(self.steering_angle) < 0.01:
            displacement = self.velocity * dt
            dx = displacement * np.cos(self.heading)
            dy = displacement * np.sin(self.heading)
            self.position += np.array([dx, dy], dtype=np.float64)
        else:
            heading_rate = self.velocity * np.tan(self.steering_angle) / 1.0
            heading_start = self.heading
            heading_mid = heading_start + heading_rate * (dt / 2.0)
            
            displacement = self.velocity * dt
            dx = displacement * np.cos(heading_mid)
            dy = displacement * np.sin(heading_mid)
            self.position += np.array([dx, dy], dtype=np.float64)
            
            self.heading = heading_start + heading_rate * dt
            self.heading = np.arctan2(np.sin(self.heading), np.cos(self.heading))
    
    def reset(self):
        """Reset system"""
        self.position = np.array([INITIAL_X, INITIAL_Y], dtype=np.float64)
        self.heading = INITIAL_HEADING
        self.velocity = 0.0
        self.steering_angle = 0.0
        self.rpm = 0.0
        self.lap_counter.reset()
        if ENABLE_PI_FILTER:
            self.pi_steering.reset()


# Sample test tracks - Closed loop circuits with specific turn angles
TEST_TRACKS = {
    'circuit_alpha': {
        'name': 'Circuit Alpha',
        'description': 'Balanced track: 60° and 90° turns with long straights',
        'duration': 100,
        'data': lambda t: (
            # Closed loop: Start → Straight → 60° right → Straight → 90° left → Straight → 60° right → Return
            np.radians(60) if (15 < (t % 50) < 20) else      # Turn 1: 60° right
            np.radians(-90) if (28 < (t % 50) < 35) else     # Turn 2: 90° left
            np.radians(60) if (42 < (t % 50) < 47) else      # Turn 3: 60° right
            0,  # Straights
            380
        )
    },
    'circuit_beta': {
        'name': 'Circuit Beta',
        'description': 'Technical track: 30°, 45°, and 120° combinations',
        'duration': 110,
        'data': lambda t: (
            # Closed loop with varied turns
            np.radians(30) if (12 < (t % 55) < 16) else      # Turn 1: 30° right (gentle)
            np.radians(45) if (22 < (t % 55) < 27) else      # Turn 2: 45° right
            np.radians(-120) if (35 < (t % 55) < 43) else    # Turn 3: 120° left (hairpin)
            np.radians(45) if (48 < (t % 55) < 52) else      # Turn 4: 45° right (return)
            0,
            350
        )
    },
    'circuit_gamma': {
        'name': 'Circuit Gamma',
        'description': 'High-speed track: 45° and 90° sweepers',
        'duration': 90,
        'data': lambda t: (
            # Fast flowing circuit
            np.radians(45) if (10 < (t % 45) < 15) else      # Turn 1: 45° right
            np.radians(90) if (22 < (t % 45) < 29) else      # Turn 2: 90° right
            np.radians(45) if (35 < (t % 45) < 40) else      # Turn 3: 45° right
            0,
            420
        )
    },
    'circuit_delta': {
        'name': 'Circuit Delta',
        'description': 'Challenging track: 145° hairpin and 60° chicane',
        'duration': 120,
        'data': lambda t: (
            # Technical circuit with hairpin
            np.radians(60) if (14 < (t % 60) < 18) else      # Turn 1: 60° right
            np.radians(-60) if (18 < (t % 60) < 22) else     # Turn 2: 60° left (chicane)
            np.radians(-145) if (32 < (t % 60) < 42) else    # Turn 3: 145° left (hairpin)
            np.radians(90) if (50 < (t % 60) < 56) else      # Turn 4: 90° right (return)
            0,
            340
        )
    },
    'circuit_omega': {
        'name': 'Circuit Omega',
        'description': 'Mixed track: All turn types (30°-145°)',
        'duration': 130,
        'data': lambda t: (
            # Complete variety circuit
            np.radians(30) if (10 < (t % 65) < 13) else      # Turn 1: 30° right
            np.radians(90) if (20 < (t % 65) < 27) else      # Turn 2: 90° right
            np.radians(-120) if (35 < (t % 65) < 43) else    # Turn 3: 120° left
            np.radians(45) if (48 < (t % 65) < 52) else      # Turn 4: 45° right
            np.radians(60) if (57 < (t % 65) < 61) else      # Turn 5: 60° right (return)
            0,
            360
        )
    }
}


def run_test_track(track_name):
    """Run a test track simulation"""
    global test_state
    
    if track_name not in TEST_TRACKS:
        return
    
    track = TEST_TRACKS[track_name]
    system = TestingSystem()
    
    with state_lock:
        test_state['running'] = True
        test_state['path_points'] = []
        test_state['selected_track'] = track_name
        test_state['reference_lap_distance'] = 0.0
    
    duration = track['duration']
    dt = 0.2  # Fixed dt as requested
    
    for step in range(int(duration / dt)):
        if not test_state['running']:
            break
        
        t = step * dt
        steering, rpm = track['data'](t)
        
        pos, heading, vel, laps, lap_dist, total_dist = system.update(steering, rpm)
        
        # Get lap info including reference lap distance
        lap_info = system.lap_counter.get_lap_info()
        
        with state_lock:
            test_state['x'] = float(pos[0])
            test_state['y'] = float(pos[1])
            test_state['heading'] = float(heading)
            test_state['velocity'] = float(vel)
            test_state['steering_angle'] = float(system.steering_angle)
            test_state['rpm'] = float(rpm)
            test_state['laps_completed'] = int(laps)
            test_state['current_lap_distance'] = float(lap_dist)
            test_state['total_distance'] = float(total_dist)
            test_state['reference_lap_distance'] = float(lap_info['reference_lap_distance'])
            test_state['path_points'].append({'x': float(pos[0]), 'y': float(pos[1])})
        
        time.sleep(dt)
    
    with state_lock:
        test_state['running'] = False


@app.get("/")
async def get_dashboard():
    """Serve testing dashboard HTML"""
    with open('templates/test_dashboard.html', 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


@app.get("/display")
async def get_5inch_display():
    """Serve 5-inch display HTML (simulates hardware display)"""
    with open('templates/display_5inch.html', 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            with state_lock:
                await websocket.send_json(test_state)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.get("/api/tracks")
async def get_tracks():
    """Get available test tracks"""
    return {
        name: {'name': track['name'], 'description': track['description']}
        for name, track in TEST_TRACKS.items()
    }


@app.post("/api/start/{track_name}")
async def start_track(track_name: str):
    """Start a test track"""
    if track_name in TEST_TRACKS:
        thread = threading.Thread(target=run_test_track, args=(track_name,), daemon=True)
        thread.start()
        return {"status": "started", "track": track_name}
    return {"status": "error", "message": "Track not found"}


@app.post("/api/stop")
async def stop_track():
    """Stop current test"""
    with state_lock:
        test_state['running'] = False
    return {"status": "stopped"}


@app.post("/api/reset")
async def reset_system():
    """Reset the system"""
    with state_lock:
        test_state['x'] = 0.0
        test_state['y'] = 0.0
        test_state['heading'] = 0.0
        test_state['velocity'] = 0.0
        test_state['steering_angle'] = 0.0
        test_state['rpm'] = 0.0
        test_state['laps_completed'] = 0
        test_state['current_lap_distance'] = 0.0
        test_state['total_distance'] = 0.0
        test_state['reference_lap_distance'] = 0.0
        test_state['path_points'] = []
        test_state['running'] = False
    return {"status": "reset"}


if __name__ == "__main__":
    import asyncio
    print("="*60)
    print("Hardware Testing Server - Dead Reckoning System")
    print("="*60)
    print("Testing Configuration:")
    print(f"  - Steering Sensor: AS5600 (simulated)")
    print(f"  - RPM Sensor: AS314 (simulated)")
    print(f"  - Update Rate: dt = 0.2s (5 Hz)")
    print(f"  - PI Filter: {'Enabled' if ENABLE_PI_FILTER else 'Disabled'}")
    print(f"  - Integration: {'RK2' if USE_RK2_INTEGRATION else 'Euler'}")
    print("="*60)
    print("\nServer: http://127.0.0.1:8888")
    print("5\" Display: http://127.0.0.1:8888/display")
    print("="*60)
    
    uvicorn.run(app, host='127.0.0.1', port=8888, log_level="info")
