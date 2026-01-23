import cv2
import time
import os
import torch
import winsound
from ultralytics import YOLO
from twilio.rest import Client

# ================= CONFIG =================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PERSON_MODEL = YOLO("yolov8n.pt").to(DEVICE)
WEAPON_MODEL = YOLO("models/weapon.pt").to(DEVICE)
ANIMAL_CLS_MODEL = YOLO("yolov8m-cls.pt").to(DEVICE)

ZONE = "Forest-Zone-A"
CAMERA_ID = "CAM-01"

# Twilio credentials - use environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = "+12566990397"
TWILIO_TO = "+919345767128"

ALERT_COOLDOWN = 30
last_alert = 0

# ================= ALERT FUNCTIONS =================
def send_sms(msg):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(body=msg, from_=TWILIO_FROM, to=TWILIO_TO)
        print("📩 SMS SENT")
    except Exception as e:
        print("SMS ERROR:", e)

def play_alarm():
    winsound.Beep(2200, 1500)

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
print("✅ Wild Vision Started (Press Q to exit)")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    weapon_found = False
    animal_found = False
    animal_species = "Unknown"

    # ---------- PERSON DETECTION ----------
    p_results = PERSON_MODEL(frame, conf=0.4, verbose=False)
    for r in p_results:
        for box in r.boxes:
            if PERSON_MODEL.names[int(box.cls[0])] == "person":
                person_found = True
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,"PERSON",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

    # ---------- WEAPON DETECTION ----------
    w_results = WEAPON_MODEL(frame, conf=0.45, verbose=False)
    for r in w_results:
        for box in r.boxes:
            weapon_found = True
            wname = WEAPON_MODEL.names[int(box.cls[0])]
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv2.putText(frame,wname.upper(),(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)

    # ---------- ANIMAL SPECIES (CROP + CLASSIFY) ----------
    a_results = PERSON_MODEL(frame, conf=0.25, verbose=False)
    for r in a_results:
        for box in r.boxes:
            if PERSON_MODEL.names[int(box.cls[0])] == "animal":
                animal_found = True
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                crop = frame[y1:y2, x1:x2]
                if crop.size > 0:
                    cls = ANIMAL_CLS_MODEL(crop, verbose=False)[0]
                    animal_species = ANIMAL_CLS_MODEL.names[int(cls.probs.top1)]
                cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
                cv2.putText(frame,animal_species.upper(),(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)

    # ---------- REAL POACHING ALERT ----------
    if person_found and weapon_found and animal_found:
        now = time.time()
        if now - last_alert > ALERT_COOLDOWN:
            msg = (
                f"🚨 POACHING ALERT\n"
                f"Animal: {animal_species}\n"
                f"Weapon Detected\n"
                f"Zone: {ZONE}\n"
                f"Camera: {CAMERA_ID}"
            )
            print(msg)
            play_alarm()
            send_sms(msg)
            last_alert = now

    cv2.imshow("Wild Vision – Exact Poaching Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
