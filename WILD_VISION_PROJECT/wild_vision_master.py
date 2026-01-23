
import cv2
import time
import torch
import winsound
from ultralytics import YOLO
from twilio.rest import Client

# ===================== CONFIG =====================
WEAPON_MODEL_PATH = "models/weapon.pt"

CONF_PERSON = 0.5
CONF_WEAPON = 0.5
CONF_ANIMAL = 0.6
ALERT_COOLDOWN = 20  # seconds

# -------- Twilio SMS --------
# Use environment variables for credentials
import os
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")
# ================================================

device = "cuda" if torch.cuda.is_available() else "cpu"
print("🖥 Device:", device)

print("🔄 Loading models...")
person_model = YOLO("yolov8n.pt").to(device)
animal_model = YOLO("yolov8n-cls.pt").to(device)

weapon_model = None
try:
    weapon_model = YOLO(WEAPON_MODEL_PATH).to(device)
    print("✅ Weapon model loaded")
except:
    print("❌ Weapon model not found")

def send_sms(msg):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=msg,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("📨 SMS sent")
    except Exception as e:
        print("❌ SMS error:", e)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Camera not available")
    exit()

print("✅ Wild Vision Started (Press Q to exit)")
last_alert = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    animal_found = False
    weapon_found = False
    animal_name = ""
    weapon_name = ""

    # -------- PERSON DETECTION --------
    p_results = person_model(frame, conf=CONF_PERSON, verbose=False)
    for r in p_results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if person_model.names[cls] == "person":
                person_found = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)
                cv2.putText(frame, "Person", (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # -------- WEAPON DETECTION --------
    if weapon_model:
        w_results = weapon_model(frame, conf=CONF_WEAPON, verbose=False)
        for r in w_results:
            for box in r.boxes:
                weapon_found = True
                cls = int(box.cls[0])
                weapon_name = weapon_model.names[cls]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, weapon_name, (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    # -------- ANIMAL CLASSIFICATION --------
    a_results = animal_model(frame, conf=CONF_ANIMAL, verbose=False)
    for r in a_results:
        cls = int(r.probs.top1)
        animal_name = animal_model.names[cls]
        animal_found = True
        cv2.putText(frame, f"Animal: {animal_name}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    # -------- POACHING ALERT --------
    if person_found and animal_found and weapon_found:
        if time.time() - last_alert > ALERT_COOLDOWN:
            alert_msg = f"POACHING ALERT! Person + {animal_name} + {weapon_name}"
            print("🚨", alert_msg)
            winsound.Beep(2000, 1000)
            send_sms(alert_msg)
            last_alert = time.time()

    cv2.imshow("Wild Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
| Out-File wild_vision_master.py -Encoding utf8
