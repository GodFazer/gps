from flask import Flask, render_template, jsonify
import asyncio
import websockets
import json

app = Flask(__name__)

# WebSocket client
async def gps_data():
    uri = "ws://localhost:4001"  # WebSocket server URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            yield json.loads(data)

# Flask route for the web page
@app.route('/')
def index():
    return render_template('index.html')

# API route to get GPS data
@app.route('/gps_data', methods=['GET'])
async def gps_stream():
    async for data in gps_data():
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, jsonify
import asyncio
import websockets
import json

app = Flask(__name__)

# WebSocket client
async def gps_data():
    uri = "ws://localhost:4001"  # WebSocket server URL
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            yield json.loads(data)

# Flask route for the web page
@app.route('/')
def index():
    return render_template('index.html')

# API route to get GPS data
@app.route('/gps_data', methods=['GET'])
async def gps_stream():
    async for data in gps_data():
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
