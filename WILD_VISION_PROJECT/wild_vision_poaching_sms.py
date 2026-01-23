import cv2
import time
import torch
import os
from ultralytics import YOLO
from twilio.rest import Client
from datetime import datetime

# ==============================
# TWILIO CONFIG (USE SAME AS SMS TEST)
# ==============================
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = "+12566990397"     # Twilio number
TWILIO_TO = "+919345767128"      # Your phone number

client = Client(TWILIO_SID, TWILIO_TOKEN)

def send_poaching_sms(msg):
    try:
        message = client.messages.create(
            body=msg,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("✅ POACHING SMS SENT:", message.sid)
    except Exception as e:
        print("❌ SMS FAILED:", e)

# ==============================
# LOAD MODELS
# ==============================
print("🔄 Loading models...")

device = "cuda" if torch.cuda.is_available() else "cpu"

person_model = YOLO("yolov8n.pt").to(device)        # person
animal_model = YOLO("yolov8n.pt").to(device)        # animals
weapon_model = YOLO("models/weapon.pt").to(device)  # weapon

print("✅ Models loaded on", device)

# ==============================
# CAMERA
# ==============================
cap = cv2.VideoCapture(0)
assert cap.isOpened(), "❌ Camera not opening"

last_sms_time = 0
SMS_COOLDOWN = 60  # seconds

print("🎥 Live detection started (Press Q to exit)")

# ==============================
# MAIN LOOP
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    animal_found = None
    weapon_found = None

    # ---- PERSON DETECTION ----
    results_person = person_model(frame, conf=0.5, verbose=False)
    for r in results_person:
        for box in r.boxes:
            cls = int(box.cls[0])
            if person_model.names[cls] == "person":
                person_found = True
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,"PERSON",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

    # ---- ANIMAL DETECTION ----
    results_animal = animal_model(frame, conf=0.5, verbose=False)
    for r in results_animal:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = animal_model.names[cls]
            if label not in ["person", "car", "truck"]:
                animal_found = label.upper()
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,0),2)
                cv2.putText(frame,animal_found,(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)

    # ---- WEAPON DETECTION ----
    results_weapon = weapon_model(frame, conf=0.4, verbose=False)
    for r in results_weapon:
        for box in r.boxes:
            cls = int(box.cls[0])
            weapon_found = weapon_model.names[cls].upper()
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv2.putText(frame,weapon_found,(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)

    # ==============================
    # POACHING LOGIC
    # ==============================
    if person_found and animal_found and weapon_found:
        cv2.putText(frame,"🚨 POACHING DETECTED 🚨",
                    (30,40),cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),3)

        now = time.time()
        if now - last_sms_time > SMS_COOLDOWN:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sms_text = (
                f"🚨 POACHING ALERT 🚨\n"
                f"Animal: {animal_found}\n"
                f"Weapon: {weapon_found}\n"
                f"Time: {timestamp}\n"
                f"Location: Camera-1"
            )
            send_poaching_sms(sms_text)
            last_sms_time = now

    # ---- SHOW WINDOW ----
    cv2.imshow("Wild Vision – Poaching Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ==============================
# CLEANUP
# ==============================
cap.release()
cv2.destroyAllWindows()
print("🛑 System stopped")
