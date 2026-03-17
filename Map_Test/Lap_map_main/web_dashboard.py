#!/usr/bin/env python3
"""
Real-time web dashboard for vehicle state display
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dead_reckoning_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state shared with main system
vehicle_state = {
    'x': 0.0,
    'y': 0.0,
    'heading': 0.0,
    'velocity': 0.0,
    'rpm': 0.0,
    'steering_angle': 0.0,
    'laps_completed': 0,
    'current_lap_distance': 0.0,
    'total_distance': 0.0,
    'path_points': []
}

state_lock = threading.Lock()


def update_vehicle_state(x, y, heading, velocity, rpm, steering_angle, 
                         laps, lap_distance, total_distance):
    """Update vehicle state from main system"""
    with state_lock:
        vehicle_state['x'] = x
        vehicle_state['y'] = y
        vehicle_state['heading'] = heading
        vehicle_state['velocity'] = velocity
        vehicle_state['rpm'] = rpm
        vehicle_state['steering_angle'] = steering_angle
        vehicle_state['laps_completed'] = laps
        vehicle_state['current_lap_distance'] = lap_distance
        vehicle_state['total_distance'] = total_distance
        
        # Keep last 500 points for path visualization
        vehicle_state['path_points'].append({'x': x, 'y': y})
        if len(vehicle_state['path_points']) > 500:
            vehicle_state['path_points'].pop(0)


@app.route('/')
def index():
    """Serve dashboard HTML"""
    return render_template('dashboard.html')


@app.route('/api/state')
def get_state():
    """API endpoint for current state"""
    with state_lock:
        return jsonify(vehicle_state)


def emit_state_updates():
    """Background thread to emit state updates via WebSocket"""
    while True:
        time.sleep(0.1)  # 10 Hz update rate
        with state_lock:
            socketio.emit('state_update', vehicle_state)


def start_dashboard(host='0.0.0.0', port=5000):
    """Start the web dashboard server"""
    # Start background thread for state updates
    update_thread = threading.Thread(target=emit_state_updates, daemon=True)
    update_thread.start()
    
    print(f"\n{'='*50}")
    print(f"Dashboard running at: http://{host}:{port}")
    print(f"{'='*50}\n")
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    start_dashboard()
