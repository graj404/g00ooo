#!/usr/bin/env python3
"""
Manual input server for testing dead reckoning without hardware
Provides web interface to input SAS and velocity manually
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import threading
import time
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_input_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Manual input values
manual_inputs = {
    'steering_angle_deg': 0.0,
    'velocity_ms': 0.0,
    'rpm': 0.0
}

input_lock = threading.Lock()


@app.route('/input')
def input_page():
    """Serve manual input page"""
    return render_template('manual_input.html')


@app.route('/api/set_input', methods=['POST'])
def set_input():
    """API to set manual input values"""
    data = request.json
    with input_lock:
        if 'steering_angle_deg' in data:
            manual_inputs['steering_angle_deg'] = float(data['steering_angle_deg'])
        if 'velocity_ms' in data:
            manual_inputs['velocity_ms'] = float(data['velocity_ms'])
            # Calculate RPM from velocity (assuming 0.2m wheel diameter)
            wheel_circumference = 0.2 * np.pi
            manual_inputs['rpm'] = (manual_inputs['velocity_ms'] / wheel_circumference) * 60.0
    return jsonify({'success': True, 'inputs': manual_inputs})


@app.route('/api/get_input')
def get_input():
    """API to get current manual input values"""
    with input_lock:
        return jsonify(manual_inputs)


def get_manual_steering_angle():
    """Get steering angle in radians"""
    with input_lock:
        return np.radians(manual_inputs['steering_angle_deg'])


def get_manual_velocity():
    """Get velocity in m/s"""
    with input_lock:
        return manual_inputs['velocity_ms']


def get_manual_rpm():
    """Get RPM"""
    with input_lock:
        return manual_inputs['rpm']


def start_input_server(host='0.0.0.0', port=5001):
    """Start the manual input server"""
    print(f"\n{'='*50}")
    print(f"Manual Input Server: http://{host}:{port}/input")
    print(f"{'='*50}\n")
    
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    start_input_server()
