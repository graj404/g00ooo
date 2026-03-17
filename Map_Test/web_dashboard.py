#!/usr/bin/env python3
"""
Real-time web dashboard for vehicle state display (Testing - Detailed)
FastAPI + WebSocket
Shows: All sensor data, calculations, detailed metrics
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import threading
from pathlib import Path

app = FastAPI()

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
    'dt': 0.0,
    'fuel_level': 100.0,
    'path_points': []
}

state_lock = threading.Lock()
connected_clients = []


def update_vehicle_state(x, y, heading, velocity, rpm, steering_angle, 
                         laps, lap_distance, total_distance, dt, fuel_level=None):
    """Update vehicle state from main system (detailed for testing)"""
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
        vehicle_state['dt'] = dt
        
        if fuel_level is not None:
            vehicle_state['fuel_level'] = fuel_level
        
        # Keep last 500 points
        vehicle_state['path_points'].append({'x': x, 'y': y})
        if len(vehicle_state['path_points']) > 500:
            vehicle_state['path_points'].pop(0)


@app.get("/")
async def get_dashboard():
    """Serve detailed testing dashboard HTML"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Testing Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #0f0;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            color: #0f0;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: #000;
            border: 2px solid #0f0;
            border-radius: 5px;
            padding: 15px;
        }
        .card h2 {
            font-size: 16px;
            color: #0f0;
            margin-bottom: 10px;
            border-bottom: 1px solid #0f0;
            padding-bottom: 5px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }
        .metric-label {
            color: #0a0;
        }
        .metric-value {
            color: #0f0;
            font-weight: bold;
        }
        .map-container {
            height: 400px;
            position: relative;
        }
        #map {
            width: 100%;
            height: 100%;
            background: #000;
            border: 2px solid #0f0;
        }
        .lap-counter {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 255, 0, 0.2);
            border: 2px solid #0f0;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 32px;
            font-weight: bold;
        }
        .lap-label {
            font-size: 14px;
            margin-bottom: 5px;
        }
        .input-section {
            background: #000;
            border: 2px solid #0f0;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .input-group {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 10px;
        }
        .input-field {
            display: flex;
            flex-direction: column;
        }
        .input-field label {
            color: #0a0;
            font-size: 12px;
            margin-bottom: 5px;
        }
        .input-field input {
            background: #000;
            border: 1px solid #0f0;
            color: #0f0;
            padding: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        button {
            background: #0f0;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        button:hover {
            background: #0a0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 VEHICLE TESTING DASHBOARD</h1>
        
        <div class="input-section">
            <h2>MANUAL INPUT CONTROLS</h2>
            <div class="input-group">
                <div class="input-field">
                    <label>Steering Angle (degrees)</label>
                    <input type="number" id="input-steering" value="0" step="1">
                </div>
                <div class="input-field">
                    <label>Velocity (m/s)</label>
                    <input type="number" id="input-velocity" value="0" step="0.1">
                </div>
                <div class="input-field">
                    <label>Fuel Level (%)</label>
                    <input type="number" id="input-fuel" value="100" step="1" min="0" max="100">
                </div>
            </div>
            <div style="margin-top: 15px;">
                <button onclick="sendManualInput()">UPDATE SENSORS</button>
                <button onclick="resetPosition()" style="margin-left: 10px;">RESET POSITION</button>
            </div>
        </div>
        
        <div class="grid">
            <div>
                <div class="card" style="margin-bottom: 20px;">
                    <h2>SENSOR INPUTS</h2>
                    <div class="metric">
                        <span class="metric-label">SAS (Steering):</span>
                        <span class="metric-value" id="sas">0.0°</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Velocity:</span>
                        <span class="metric-value" id="velocity">0.00 m/s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">RPM:</span>
                        <span class="metric-value" id="rpm">0 rpm</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Fuel Level:</span>
                        <span class="metric-value" id="fuel">100%</span>
                    </div>
                </div>
                
                <div class="card" style="margin-bottom: 20px;">
                    <h2>CALCULATIONS</h2>
                    <div class="metric">
                        <span class="metric-label">Δt (delta time):</span>
                        <span class="metric-value" id="dt">0.000 s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Heading:</span>
                        <span class="metric-value" id="heading">0.0°</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Distance (step):</span>
                        <span class="metric-value" id="step-dist">0.000 m</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>POSITION & DISTANCE</h2>
                    <div class="metric">
                        <span class="metric-label">Position X:</span>
                        <span class="metric-value" id="pos-x">0.00 m</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Position Y:</span>
                        <span class="metric-value" id="pos-y">0.00 m</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Current Lap:</span>
                        <span class="metric-value" id="lap-distance">0.0 m</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Distance:</span>
                        <span class="metric-value" id="total-distance">0.0 m</span>
                    </div>
                </div>
            </div>
            
            <div class="card map-container">
                <h2>VEHICLE PATH MAP</h2>
                <div class="lap-counter">
                    <div class="lap-label">LAP</div>
                    <div id="lap-count">0</div>
                </div>
                <canvas id="map"></canvas>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('map');
        const ctx = canvas.getContext('2d');
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        let pathPoints = [];
        let currentPos = {x: 0, y: 0};
        let scale = 10;
        let offsetX = canvas.width / 2;
        let offsetY = canvas.height / 2;
        
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Update all metrics
            document.getElementById('sas').textContent = (data.steering_angle * 180 / Math.PI).toFixed(1) + '°';
            document.getElementById('velocity').textContent = data.velocity.toFixed(2) + ' m/s';
            document.getElementById('rpm').textContent = Math.round(data.rpm) + ' rpm';
            document.getElementById('fuel').textContent = Math.round(data.fuel_level) + '%';
            document.getElementById('dt').textContent = data.dt.toFixed(3) + ' s';
            document.getElementById('heading').textContent = (data.heading * 180 / Math.PI).toFixed(1) + '°';
            document.getElementById('step-dist').textContent = (data.velocity * data.dt).toFixed(3) + ' m';
            document.getElementById('pos-x').textContent = data.x.toFixed(2) + ' m';
            document.getElementById('pos-y').textContent = data.y.toFixed(2) + ' m';
            document.getElementById('lap-distance').textContent = data.current_lap_distance.toFixed(1) + ' m';
            document.getElementById('total-distance').textContent = data.total_distance.toFixed(1) + ' m';
            document.getElementById('lap-count').textContent = data.laps_completed;
            
            // Update position and path
            currentPos = {x: data.x, y: data.y};
            pathPoints = data.path_points;
            drawMap();
        };
        
        function sendManualInput() {
            const steering = parseFloat(document.getElementById('input-steering').value);
            const velocity = parseFloat(document.getElementById('input-velocity').value);
            const fuel = parseFloat(document.getElementById('input-fuel').value);
            
            fetch('/api/manual_input', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    steering_angle: steering * Math.PI / 180,
                    velocity: velocity,
                    fuel_level: fuel
                })
            });
        }
        
        function resetPosition() {
            fetch('/api/reset', {method: 'POST'});
        }
        
        function drawMap() {
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            if (pathPoints.length < 2) return;
            
            // Auto-scale
            const xs = pathPoints.map(p => p.x);
            const ys = pathPoints.map(p => p.y);
            const minX = Math.min(...xs);
            const maxX = Math.max(...xs);
            const minY = Math.min(...ys);
            const maxY = Math.max(...ys);
            
            const rangeX = maxX - minX || 1;
            const rangeY = maxY - minY || 1;
            const scaleX = (canvas.width - 100) / rangeX;
            const scaleY = (canvas.height - 100) / rangeY;
            scale = Math.min(scaleX, scaleY, 50);
            
            offsetX = canvas.width / 2 - (minX + maxX) / 2 * scale;
            offsetY = canvas.height / 2 + (minY + maxY) / 2 * scale;
            
            // Draw grid
            ctx.strokeStyle = '#1a1a1a';
            ctx.lineWidth = 1;
            for (let i = -50; i <= 50; i++) {
                ctx.beginPath();
                ctx.moveTo(offsetX + i * scale * 5, 0);
                ctx.lineTo(offsetX + i * scale * 5, canvas.height);
                ctx.stroke();
                
                ctx.beginPath();
                ctx.moveTo(0, offsetY - i * scale * 5);
                ctx.lineTo(canvas.width, offsetY - i * scale * 5);
                ctx.stroke();
            }
            
            // Draw start point
            ctx.fillStyle = '#0f0';
            ctx.beginPath();
            ctx.arc(offsetX, offsetY, 8, 0, 2 * Math.PI);
            ctx.fill();
            
            // Draw path
            ctx.strokeStyle = '#0f0';
            ctx.lineWidth = 3;
            ctx.beginPath();
            pathPoints.forEach((point, i) => {
                const x = offsetX + point.x * scale;
                const y = offsetY - point.y * scale;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();
            
            // Draw current position (pulsing circle)
            const x = offsetX + currentPos.x * scale;
            const y = offsetY - currentPos.y * scale;
            
            const pulseSize = 15 + Math.sin(Date.now() / 200) * 5;
            
            ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
            ctx.beginPath();
            ctx.arc(x, y, pulseSize, 0, 2 * Math.PI);
            ctx.fill();
            
            ctx.fillStyle = '#0f0';
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, 2 * Math.PI);
            ctx.fill();
        }
        
        setInterval(drawMap, 50);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            with state_lock:
                await websocket.send_json(vehicle_state)
            await asyncio.sleep(0.1)  # 10 Hz
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.post("/api/manual_input")
async def manual_input(request: Request):
    """Receive manual sensor input for testing"""
    data = await request.json()
    
    # Import main module to access dr_system
    import main as test_main
    if test_main.dr_system:
        test_main.dr_system.set_manual_input(
            data.get('steering_angle', 0.0),
            data.get('velocity', 0.0),
            data.get('fuel_level', None)
        )
    
    return {"status": "ok"}


@app.post("/api/reset")
async def reset_position():
    """Reset vehicle position"""
    import main as test_main
    if test_main.dr_system:
        test_main.dr_system.reset_position()
    return {"status": "ok"}


def start_dashboard(host='0.0.0.0', port=5000):
    """Start the web dashboard server"""
    import uvicorn
    print(f"\n{'='*50}")
    print(f"Testing Dashboard: http://{host}:{port}")
    print(f"{'='*50}\n")
    uvicorn.run(app, host=host, port=port, log_level="error")


if __name__ == "__main__":
    start_dashboard()
