import cv2
import torch
import time
import os
from ultralytics import YOLO
from flask import Flask, Response, render_template_string, request
from threading import Thread
from twilio.rest import Client
import winsound

# ========== CONFIG ==========
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
ZONE = "ZONE-A"
CAMERA_ID = 1
CONF = 0.45

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

# ============================

app = Flask(__name__)

detector = YOLO("yolov8n.pt").to(DEVICE)
weapon_model = YOLO("models/weapon.pt").to(DEVICE)

latest = {
    "status": "SAFE",
    "zone": ZONE,
    "risk": "LOW",
    "animal": "-",
    "weapon": "-"
}

sms_sent = False
frame_global = None

# -------- SMS ----------
def send_sms(msg):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=msg, from_=TWILIO_FROM, to=TWILIO_TO)
        print("SMS sent")
    except Exception as e:
        print("SMS error:", e)

# -------- ALARM --------
def alarm():
    winsound.Beep(1500, 1000)

# -------- DETECTION LOOP --------
def detect_loop():
    global frame_global, latest, sms_sent

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        humans, animals, weapons = False, [], []

        # ---- Person & Animal
        res = detector(frame, conf=CONF, verbose=False)[0]
        for box in res.boxes:
            cls = int(box.cls[0])
            name = detector.names[cls]
            x1,y1,x2,y2 = map(int, box.xyxy[0])

            if name == "person":
                humans = True
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,"Person",(x1,y1-5),0,0.6,(0,255,0),2)

            elif name in ["elephant","bear","zebra","giraffe","cow","horse","dog","cat"]:
                animals.append(name)
                cv2.rectangle(frame,(x1,y1),(x2,y2),(255,200,0),2)
                cv2.putText(frame,name,(x1,y1-5),0,0.6,(255,200,0),2)

        # ---- Weapon
        wres = weapon_model(frame, conf=0.55, verbose=False)[0]
        for box in wres.boxes:
            weapon = weapon_model.names[int(box.cls[0])]
            weapons.append(weapon)
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv2.putText(frame,weapon,(x1,y1-5),0,0.6,(0,0,255),2)

        # ---- Poaching Logic
        if humans and animals and weapons:
            latest.update({
                "status": "POACHING DETECTED",
                "animal": animals[0],
                "weapon": weapons[0],
                "risk": "HIGH"
            })

            if not sms_sent:
                alarm()
                send_sms(
                    f"🚨 POACHING ALERT\nZone: {ZONE}\nCamera: {CAMERA_ID}\n"
                    f"Animal: {animals[0]}\nWeapon: {weapons[0]}\nRisk: HIGH"
                )
                sms_sent = True

        frame_global = frame.copy()
        time.sleep(0.03)

# -------- VIDEO STREAM --------
def gen_frames():
    global frame_global
    while True:
        if frame_global is not None:
            _, buffer = cv2.imencode('.jpg', frame_global)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   buffer.tobytes() + b'\r\n')

# -------- DASHBOARD --------
HTML = """
<html>
<head>
<title>Wild Vision Dashboard</title>
<style>
body{background:#0f172a;color:white;font-family:Arial;text-align:center}
img{border:3px solid #22d3ee}
button{padding:10px;margin:10px;font-size:16px}
</style>
</head>
<body>
<h1>Wild Vision – Live Poaching Monitor</h1>

<img src="/video">

<h2>Status: {{status}}</h2>
<p>Zone: {{zone}}</p>
<p>Animal: {{animal}}</p>
<p>Weapon: {{weapon}}</p>
<p>Risk: {{risk}}</p>

<form method="post">
<button name="action" value="IN-PROGRESS">In Progress</button>
<button name="action" value="COMPLETED">Completed</button>
</form>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def dashboard():
    global latest
    if request.method == "POST":
        latest["status"] = request.form["action"]
    return render_template_string(HTML, **latest)

@app.route("/video")
def video():
    return Response(gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame')

# -------- MAIN --------
if __name__ == "__main__":
    Thread(target=detect_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
