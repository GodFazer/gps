from flask import Flask, jsonify, render_template, request
from websocket import WebSocketApp
import json
import threading
import time

app = Flask(__name__)

DATA_EXPIRATION = 4  # seconds
data_points = []

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/config', methods=['POST'])
def update_config():
    try:
        params = request.json
        emulation_zone = params.get('emulationZoneSize')
        message_rate = params.get('messageFrequency')
        satellite_velocity = params.get('satelliteSpeed')
        object_velocity = params.get('objectSpeed')

        # Дополнительная обработка параметров может быть добавлена здесь
        return jsonify({"status": "success", "message": "Configuration updated"}), 200
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.route('/data')
def fetch_data():
    if len(data_points) < 3:
        return jsonify({"status": "error", "message": "Not enough data"}), 400

    x_calc, y_calc = calculate_position(
        data_points[0]['x'], data_points[0]['y'], data_points[0]['radius'],
        data_points[1]['x'], data_points[1]['y'], data_points[1]['radius'],
        data_points[2]['x'], data_points[2]['y'], data_points[2]['radius']
    )

    return jsonify({
        "data": data_points,
        "calculated": {"x": x_calc, "y": y_calc}
    })

def on_message(ws, message):
    global data_points
    try:
        message_data = json.loads(message)
        point_id = message_data.get('id')
        x, y = message_data.get('x'), message_data.get('y')
        sent_at, received_at = message_data.get('sentAt'), message_data.get('receivedAt')

        radius = calculate_distance(sent_at, received_at)
        existing_point = next((pt for pt in data_points if pt['id'] == point_id), None)

        if existing_point:
            existing_point.update({
                'x': x, 'y': y, 'sentAt': sent_at, 'receivedAt': received_at,
                'radius': radius, 'last_updated': time.time()
            })
        else:
            data_points.append({
                'id': point_id, 'x': x, 'y': y, 'sentAt': sent_at,
                'receivedAt': received_at, 'radius': radius, 'last_updated': time.time()
            })

        current_time = time.time()
        data_points = [pt for pt in data_points if current_time - pt['last_updated'] < DATA_EXPIRATION]

    except json.JSONDecodeError:
        print("JSON parsing error:", message)

def on_open(ws):
    print("WebSocket connection established")

def on_close(ws):
    print("WebSocket connection closed")

def on_error(ws, error):
    print("WebSocket error:", error)

def calculate_distance(sent, received):
    return (((sent - received) / 1000) * 300000) / 1000

def calculate_position(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    a = 2 * (x2 - x1)
    b = 2 * (y2 - y1)
    c = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2

    d = 2 * (x3 - x2)
    e = 2 * (y3 - y2)
    f = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2

    x = (c * e - f * b) / (e * a - b * d)
    y = (c * d - a * f) / (b * d - a * e)
    return x, y

def start_websocket():
    ws = WebSocketApp(
        "ws://localhost:4001",
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

if __name__ == "__main__":
    threading.Thread(target=start_websocket).start()
    app.run(debug=True, host='0.0.0.0')
