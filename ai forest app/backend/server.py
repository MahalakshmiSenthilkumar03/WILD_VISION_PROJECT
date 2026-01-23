import requests
import time
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

WILD_VISION_BASE = "http://localhost:5000"

# Derived stats storage
stats_history = {
    "totalDetections": 0,
    "animalCount": 0,
    "humanCount": 0,
    "weaponCount": 0,
    "poachingAlerts": 0
}

# --- PROXY VIDEO STREAM ---
@app.route('/video_feed')
def video_feed():
    try:
        # Stream the response from Wild Vision
        resp = requests.get(f"{WILD_VISION_BASE}/video_feed", stream=True, timeout=5)
        
        def generate():
            for chunk in resp.iter_content(chunk_size=1024):
                yield chunk
                
        return Response(generate(), content_type=resp.headers['Content-Type'])
    except Exception as e:
        print(f"Video Proxy Error: {e}")
        return Response("Camera Offline", status=503)

# --- MONITOR API (ADAPTER) ---
@app.route('/api/forest/monitor')
def forest_monitor():
    try:
        # 1. Fetch from source
        resp = requests.get(f"{WILD_VISION_BASE}/api/detections", timeout=2)
        data = resp.json()
        
        # 2. Transform components
        detections = []
        ai_reasoning = []
        alert_level = "NORMAL"
        
        # Check source status from our perspective (if we got data, it's ACTIVE)
        camera_status = "ACTIVE"
        
        raw_detections = data.get("detections", [])
        
        for det in raw_detections:
            # Transform detection object
            d_name = det.get("name", "Unknown")
            d_type = det.get("type", "Unknown").capitalize()
            d_conf = int(det.get("confidence", 0) * 100)
            
            detections.append({
                "name": d_name,
                "type": d_type,
                "confidence": d_conf,
                "time": "Just now"
            })
            
            # Logic for Reasoning
            if det.get("alert"):
                ai_reasoning.append(f"{det['alert']} detected: {d_name}")
                alert_level = "CRITICAL"
                
                # Update global stats (simple increment for demo)
                stats_history["poachingAlerts"] += 1
                stats_history["weaponCount"] += 1
            elif d_type == "Human":
                 stats_history["humanCount"] += 1
            elif d_type == "Animal":
                 stats_history["animalCount"] += 1
                 
            stats_history["totalDetections"] += 1

        # Fallback reasoning if empty but active
        if not ai_reasoning and not detections:
            ai_reasoning.append("No active threats detected")
        elif not ai_reasoning:
             ai_reasoning.append("Monitoring active - standard patterns")

        # 3. Final Structure
        response = {
            "cameraStatus": camera_status,
            "lastUpdated": "Just now",
            "recentDetections": detections, # List of objects
            "aiReasoning": ai_reasoning,    # List of strings
            "alertLevel": alert_level
        }
        
        return jsonify(response)

    except requests.exceptions.ConnectionError:
        return jsonify({
            "cameraStatus": "OFFLINE",
            "lastUpdated": "Unknown",
            "recentDetections": [],
            "aiReasoning": ["Connection to Camera Lost"],
            "alertLevel": "OFFLINE"
        })
    except Exception as e:
        print(f"Monitor API Error: {e}")
        return jsonify({
            "cameraStatus": "ERROR",
            "lastUpdated": "Unknown",
            "recentDetections": [],
            "aiReasoning": [str(e)],
            "alertLevel": "ERROR"
        }), 500

# --- STATS API ---
@app.route('/api/forest/stats')
def forest_stats():
    # Return accumulated stats
    return jsonify(stats_history)

if __name__ == '__main__':
    print("Starting AI Forest Backend Adapter on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
