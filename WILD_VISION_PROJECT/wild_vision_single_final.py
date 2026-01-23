import cv2
import torch
import os
import time
from ultralytics import YOLO
from twilio.rest import Client
from datetime import datetime

# ==============================
# CONFIG
# ==============================
PERSON_MODEL = "yolov8n.pt"            # COCO model
WEAPON_MODEL = r"C:\AI\WILD_VISION_PROJECT\models\weapon.pt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CONF = 0.45

# ---- TWILIO (SMS) ----
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"
TWILIO_FROM = "+1234567890"
TWILIO_TO = "+91XXXXXXXXXX"

# ==============================
# SMS FUNCTION
# ==============================
def send_sms(message):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("📩 SMS SENT")
    except Exception as e:
        print("❌ SMS FAILED:", e)

# ==============================
# LOAD MODELS
# ==============================
print("🔄 Loading models...")

person_model = YOLO(PERSON_MODEL).to(DEVICE)

weapon_model = None
if os.path.exists(WEAPON_MODEL):
    weapon_model = YOLO(WEAPON_MODEL).to(DEVICE)
    print("✅ Weapon model loaded")
else:
    print("❌ Weapon model missing")

# ==============================
# CAMERA
# ==============================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("❌ Camera not accessible")

print("✅ Wild Vision Started (Press Q to exit)")

alert_sent = False

# ==============================
# MAIN LOOP
# ==============================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ALWAYS show window
    cv2.imshow("WILD VISION - FINAL", frame)
    cv2.waitKey(1)

    person_found = False
    animal_found = False
    weapon_found = False
    animal_name = None
    weapon_name = None

    # ---------------- PERSON + ANIMAL ----------------
    results = person_model(frame, conf=CONF, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = person_model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # PERSON
            if label == "person":
                person_found = True
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, "PERSON", (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                # -------- WEAPON ONLY INSIDE PERSON --------
                if weapon_model:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        w_results = weapon_model(crop, conf=0.5, verbose=False)
                        for wr in w_results:
                            for wbox in wr.boxes:
                                weapon_found = True
                                wcls = int(wbox.cls[0])
                                weapon_name = weapon_model.names[wcls]

                                wx1, wy1, wx2, wy2 = map(int, wbox.xyxy[0])
                                cv2.rectangle(frame,
                                    (x1+wx1, y1+wy1),
                                    (x1+wx2, y1+wy2),
                                    (0,0,255), 2)

                                cv2.putText(frame, f"WEAPON: {weapon_name.upper()}",
                                    (x1+wx1, y1+wy1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            # ANIMAL (ignore person class)
            elif label not in ["car","truck","bus","chair","bottle"]:
                animal_found = True
                animal_name = label.upper()
                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,0), 2)
                cv2.putText(frame, f"ANIMAL: {animal_name}",
                            (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    # ---------------- POACHING ALERT ----------------
    if person_found and animal_found and weapon_found and not alert_sent:
        alert_sent = True
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"🚨 POACHING DETECTED!\nAnimal: {animal_name}\nWeapon: {weapon_name}\nTime: {timestamp}"
        print(msg)
        send_sms(msg)
        cv2.putText(frame, "🚨 POACHING DETECTED",
                    (30,50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0,0,255), 3)

    cv2.imshow("WILD VISION - FINAL", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
