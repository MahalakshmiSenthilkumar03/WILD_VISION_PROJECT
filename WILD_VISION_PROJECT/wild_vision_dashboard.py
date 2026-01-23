import cv2
import time
import os
import threading
from datetime import datetime
from ultralytics import YOLO
from flask import Flask, Response, render_template_string

# ---------------- CONFIG ----------------
SAVE_DIR = "poaching_events"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load models
detect_model = YOLO("yolov8n.pt")        # person / weapon / animal
classify_model = YOLO("yolov8n-cls.pt")  # animal species

cap = cv2.VideoCapture(0)
latest_frame = None
events = []

# Fake GPS (replace later with real GPS)
GPS_LOCATION = "11.0168° N, 76.9558° E"

# Flask app
app = Flask(__name__)

# ---------------------------------------

def detection_loop():
    global latest_frame, events

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        results = detect_model(frame, conf=0.4)
        poaching_detected = False
        detected_animal = None

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = detect_model.names[cls]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # PERSON
                if label == "person":
                    color = (0, 0, 255)

                # WEAPON
                elif label in ["knife", "gun"]:
                    color = (0, 0, 255)
                    poaching_detected = True

                # ANIMAL -> classify
                elif label in ["dog", "cat", "horse", "cow", "sheep"]:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        cls_res = classify_model(crop)[0]
                        detected_animal = classify_model.names[cls_res.probs.top1]
                        label = f"Animal: {detected_animal}"
                    color = (0, 255, 0)

                else:
                    color = (255, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # POACHING LOGIC
        if poaching_detected and detected_animal:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = f"{SAVE_DIR}/poaching_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)

            events.append({
                "time": ts,
                "animal": detected_animal,
                "location": GPS_LOCATION,
                "image": filename
            })

        latest_frame = frame
        time.sleep(0.03)

def gen_frames():
    global latest_frame
    while True:
        if latest_frame is None:
            continue
        _, buffer = cv2.imencode(".jpg", latest_frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    html = """
    <h2>🦌 Wild Vision – Anti-Poaching Dashboard</h2>
    <img src="/video" width="720"><br><br>
    <h3>🚨 Poaching Alerts</h3>
    <ul>
    {% for e in events %}
        <li>
        <b>{{ e.time }}</b> | {{ e.animal }} |
        {{ e.location }}<br>
        <img src="/{{ e.image }}" width="300">
        </li><br>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, events=events)

@app.route("/video")
def video():
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

# ---------------- START ----------------
if __name__ == "__main__":
    threading.Thread(target=detection_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
