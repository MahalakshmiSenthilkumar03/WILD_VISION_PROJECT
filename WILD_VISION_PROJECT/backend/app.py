import cv2
import time
import json
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np

app = Flask(__name__)
CORS(app)

# Load Model
# Using yolov8n.pt from parent directory if available, else download
model_path = "../yolov8n.pt"
try:
    model = YOLO(model_path)
except Exception as e:
    print(f"Could not load local model at {model_path}, downloading standard yolov8n.pt")
    model = YOLO("yolov8n.pt")

camera = cv2.VideoCapture(0)  # Use 0 for live webcam


# Global state for latest detection
current_detections = {
    "camera_id": "CAM_01",
    "detections": [],
    "timestamp": "",
    "alerts": []
}

def get_dummy_frame():
    # Create a nice looking dummy frame with "NO SIGNAL" text
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.putText(img, "CAMERA SIGNAL LOST", (400, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    return img

def generate_frames():
    global current_detections
    while True:
        success, frame = camera.read()
        if not success:
            # Fallback to dummy frame
            frame = get_dummy_frame()
            # Add small delay to simulate frame rate
            time.sleep(0.1)
        
        # Run inference
        try:
            results = model(frame, verbose=False)
            annotated_frame = results[0].plot()
            
            # Process detections
            detections = []
            alerts = []
            
            for r in results[0].boxes:
                # ... same logic as before ...
                cls_id = int(r.cls[0])
                conf = float(r.conf[0])
                label = model.names[cls_id]
                
                det_type = "unknown"
                alert_msg = None
                
                if label in ["person"]:
                    det_type = "human"
                elif label in ["knife", "gun", "rifle", "pistol"]:
                    det_type = "weapon"
                    alert_msg = "Poaching"
                elif label in ["cat", "dog", "bear", "elephant", "bird", "horse", "sheep", "cow"]: 
                    det_type = "animal"
                
                detection = {
                    "type": det_type,
                    "name": label,
                    "confidence": round(conf, 2)
                }
                if alert_msg:
                    detection["alert"] = alert_msg
                    alerts.append(detection)
                    
                detections.append(detection)

            # Update global state
            current_detections = {
                "camera_id": "CAM_01",
                "detections": detections,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "alerts": alerts
            }
        except Exception as e:
            print(f"Inference error: {e}")
            annotated_frame = frame            

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detections')
def get_detections():
    return jsonify(current_detections)

@app.route('/api/alerts')
def get_alerts():
    return jsonify({"alerts": current_detections["alerts"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
