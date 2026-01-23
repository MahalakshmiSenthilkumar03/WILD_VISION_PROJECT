import cv2
import time
import os
from datetime import datetime
from ultralytics import YOLO
from flask import Flask, Response, render_template_string

# ---------------- CONFIG ----------------
SAVE_DIR = "poaching_events"
os.makedirs(SAVE_DIR, exist_ok=True)

# Models
detect_model = YOLO("yolov8n.pt")        # detection
classify_model = YOLO("yolov8n-cls.pt")  # classification

# Camera
cap = cv2.VideoCapture(0)

# Flask app
app = Flask(__name__)
latest_frame = None

# ----------------------------------------

def detect_loop():
    global latest_frame

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = detect_model(frame, conf=0.4)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = detect_model.names[cls]

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # PERSON
                if label == "person":
                    color = (0, 0, 255)

                # ANIMAL → classify
                elif label in ["dog", "cat", "horse", "sheep", "cow"]:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size == 0:
                        continue

                    cls_result = classify_model(crop)[0]
                    species = classify_model.names[cls_result.probs.top1]
                    label = f"Animal: {species}"
                    color = (0, 255, 0)

                else:
                    color = (255, 255, 0)

                cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
                cv2.putText(frame, label, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # Poaching condition
                if "person" in label.lower() and "animal" in label.lower():
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"{SAVE_DIR}/poaching_{ts}.jpg", frame)

        latest_frame = frame
        time.sleep(0.03)

def gen_frames():
    global latest_frame
    while True:
        if latest_frame is None:
            continue
        _, buffer = cv2.imencode('.jpg', latest_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route("/")
def dashboard():
    return render_template_string("""
    <h2>🦌 Wild Vision – Anti Poaching Dashboard</h2>
    <img src="/video">
    <p>Live Detection • Time-stamped Events • Auto Saved</p>
    """)

@app.route("/video")
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# ---------------- START ----------------
if __name__ == "__main__":
    import threading
    t = threading.Thread(target=detect_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
