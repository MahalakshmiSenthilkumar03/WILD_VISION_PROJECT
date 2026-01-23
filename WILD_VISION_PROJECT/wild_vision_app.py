import cv2
import time
import os
import threading
from datetime import datetime
from ultralytics import YOLO
from flask import Flask, Response, render_template_string

# ---------------- CONFIG ----------------
CAMERA_ID = 1
CAMERA_NAME = "CAM-01"
FOREST_DIVIDER_X = 320   # Inner / Outer forest divider
GPS_LOCATION = "11.0168° N, 76.9558° E"

SAVE_DIR = "poaching_events"
os.makedirs(SAVE_DIR, exist_ok=True)

# Models
detect_model = YOLO("yolov8n.pt")
classify_model = YOLO("yolov8n-cls.pt")

# Camera
cap = cv2.VideoCapture(0)

latest_frame = None
events = []
lock = threading.Lock()

# Flask
app = Flask(__name__)

# --------------------------------------------------

def detection_engine():
    global latest_frame, events

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        results = detect_model(frame, conf=0.45)
        person, weapon, animal_name = False, False, None
        zone = "Unknown"

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = detect_model.names[cls]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                zone = "INNER FOREST" if x1 < FOREST_DIVIDER_X else "OUTER FOREST"

                if label == "person":
                    person = True
                    color = (0, 0, 255)

                elif label in ["knife", "gun"]:
                    weapon = True
                    color = (0, 0, 255)

                elif label in ["dog", "horse", "cow", "sheep", "cat"]:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        res = classify_model(crop)[0]
                        animal_name = classify_model.names[res.probs.top1]
                    color = (0, 255, 0)
                    label = f"Animal: {animal_name}"

                else:
                    color = (255, 255, 0)

                cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
                cv2.putText(frame, label, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Poaching condition
        if (person and animal_name) or (person and weapon):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img_name = f"{SAVE_DIR}/poaching_{int(time.time())}.jpg"
            cv2.imwrite(img_name, frame)

            events.append({
                "time": ts,
                "animal": animal_name or "Unknown",
                "zone": zone,
                "camera": CAMERA_NAME,
                "location": GPS_LOCATION,
                "image": img_name
            })

        with lock:
            latest_frame = frame.copy()

        # CMD WINDOW
        cv2.imshow("Wild Vision – CMD Monitor", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# --------------------------------------------------

def gen_frames():
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                continue
            ret, buffer = cv2.imencode(".jpg", latest_frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")

# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    html = """
<!DOCTYPE html>
<html>
<head>
<title>Wild Vision</title>
<style>
body { background:#0f172a; color:white; font-family:Arial; }
.nav { padding:15px; background:#020617; }
.nav a { color:#38bdf8; margin:15px; text-decoration:none; font-weight:bold; }
.card { background:#020617; padding:15px; margin:15px; border-radius:12px; }
img { border-radius:10px; }
</style>
</head>

<body>
<div class="nav">
<a href="/">Live Monitor</a>
<a href="/events">Poaching Events</a>
</div>

<div class="card">
<h2>🎥 Live Monitoring – {{camera}}</h2>
<img src="/video" width="800">
</div>
</body>
</html>
"""
    return render_template_string(html, camera=CAMERA_NAME)

@app.route("/events")
def event_list():
    html = """
<!DOCTYPE html>
<html>
<body style="background:#020617;color:white;font-family:Arial">
<h2>🚨 Poaching Alerts</h2>
{% for e in events %}
<div style="background:#0f172a;padding:15px;margin:10px;border-radius:12px">
<b>{{e.time}}</b><br>
Animal: {{e.animal}}<br>
Zone: {{e.zone}}<br>
Camera: {{e.camera}}<br>
Location: {{e.location}}<br>
<img src="/{{e.image}}" width="350">
</div>
{% endfor %}
</body>
</html>
"""
    return render_template_string(html, events=events)

@app.route("/video")
def video():
    return Response(gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

# --------------------------------------------------

if __name__ == "__main__":
    threading.Thread(target=detection_engine, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
