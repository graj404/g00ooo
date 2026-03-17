#!/usr/bin/env python3
"""
Real-time web dashboard for vehicle state display (Hardware - Minimal)
FastAPI + WebSocket for 5" display
Shows: Map, Lap Count (top right), Current Position Circle, Fuel Level
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
    'laps_completed': 0,
    'fuel_level': 100.0,  # Percentage (0-100)
    'path_points': []
}

state_lock = threading.Lock()
connected_clients = []


def update_vehicle_state(x, y, laps, fuel_level=None):
    """Update vehicle state from main system (minimal for hardware)"""
    with state_lock:
        vehicle_state['x'] = x
        vehicle_state['y'] = y
        vehicle_state['laps_completed'] = laps
        
        if fuel_level is not None:
            vehicle_state['fuel_level'] = fuel_level
        
        # Keep last 500 points for path visualization
        vehicle_state['path_points'].append({'x': x, 'y': y})
        if len(vehicle_state['path_points']) > 500:
            vehicle_state['path_points'].pop(0)


@app.get("/")
async def get_dashboard():
    """Serve minimal hardware dashboard HTML"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: #000;
            color: #0f0;
            overflow: hidden;
            width: 800px;
            height: 480px;
        }
        #map {
            width: 100%;
            height: 100%;
            background: #000;
        }
        .lap-counter {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 0, 0.2);
            border: 3px solid #0f0;
            border-radius: 10px;
            padding: 15px 25px;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            min-width: 150px;
        }
        .lap-label {
            font-size: 20px;
            margin-bottom: 5px;
        }
        .fuel-indicator {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 255, 0, 0.2);
            border: 3px solid #0f0;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 24px;
            font-weight: bold;
        }
        .fuel-bar {
            width: 100px;
            height: 20px;
            background: #222;
            border: 2px solid #0f0;
            border-radius: 5px;
            margin-top: 5px;
            overflow: hidden;
        }
        .fuel-fill {
            height: 100%;
            background: #0f0;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <canvas id="map"></canvas>
    
    <div class="lap-counter">
        <div class="lap-label">LAP</div>
        <div id="lap-count">0</div>
    </div>
    
    <div class="fuel-indicator">
        <div>FUEL</div>
        <div class="fuel-bar">
            <div class="fuel-fill" id="fuel-fill" style="width: 100%"></div>
        </div>
        <div id="fuel-percent" style="text-align: center; margin-top: 5px;">100%</div>
    </div>

    <script>
        const canvas = document.getElementById('map');
        const ctx = canvas.getContext('2d');
        canvas.width = 800;
        canvas.height = 480;
        
        let pathPoints = [];
        let currentPos = {x: 0, y: 0};
        let scale = 10;
        let offsetX = canvas.width / 2;
        let offsetY = canvas.height / 2;
        
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Update lap count
            document.getElementById('lap-count').textContent = data.laps_completed;
            
            // Update fuel
            const fuelPercent = Math.round(data.fuel_level);
            document.getElementById('fuel-fill').style.width = fuelPercent + '%';
            document.getElementById('fuel-percent').textContent = fuelPercent + '%';
            
            // Update fuel color based on level
            const fuelFill = document.getElementById('fuel-fill');
            if (fuelPercent < 20) {
                fuelFill.style.background = '#f00';
            } else if (fuelPercent < 50) {
                fuelFill.style.background = '#ff0';
            } else {
                fuelFill.style.background = '#0f0';
            }
            
            // Update position and path
            currentPos = {x: data.x, y: data.y};
            pathPoints = data.path_points;
            drawMap();
        };
        
        function drawMap() {
            // Clear canvas
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
            
            // Draw current position (large circle)
            const x = offsetX + currentPos.x * scale;
            const y = offsetY - currentPos.y * scale;
            
            // Pulsing effect
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
        
        // Animation loop for pulsing effect
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
            # Send state updates
            with state_lock:
                await websocket.send_json(vehicle_state)
            await asyncio.sleep(0.1)  # 10 Hz update rate
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


def start_dashboard(host='0.0.0.0', port=5000):
    """Start the web dashboard server"""
    import uvicorn
    print(f"\n{'='*50}")
    print(f"Hardware Dashboard: http://{host}:{port}")
    print(f"{'='*50}\n")
    uvicorn.run(app, host=host, port=port, log_level="error")


if __name__ == "__main__":
    start_dashboard()
