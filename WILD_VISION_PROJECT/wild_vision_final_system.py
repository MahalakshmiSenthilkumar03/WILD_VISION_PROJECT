import cv2
import time
import winsound
from ultralytics import YOLO
from twilio.rest import Client
from datetime import datetime
import os

# =========================
# CONFIG
# =========================
CAMERA_ID = 0
DEVICE = "cuda"  # use GPU
CONF_DET = 0.4
CONF_CLS = 0.6

WEAPON_MODEL_PATH = r"C:\AI\WILD_VISION_PROJECT\models\weapon.pt"
DETECT_MODEL_PATH = r"C:\AI\WILD_VISION_PROJECT\yolov8n.pt"
CLASSIFIER_MODEL_PATH = r"C:\AI\WILD_VISION_PROJECT\yolov8n-cls.pt"

# Twilio (USE YOUR REAL VALUES)
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"
TWILIO_FROM = "+1XXXXXXXXXX"
TWILIO_TO = "+91XXXXXXXXXX"

# Protected animals
PROTECTED_SPECIES = [
    "lion", "tiger", "elephant", "leopard",
    "cheetah", "bear", "rhino", "deer"
]

# =========================
# LOAD MODELS
# =========================
print("🔄 Loading models...")

detect_model = YOLO(DETECT_MODEL_PATH)
cls_model = YOLO(CLASSIFIER_MODEL_PATH)

weapon_model = None
if os.path.exists(WEAPON_MODEL_PATH):
    weapon_model = YOLO(WEAPON_MODEL_PATH)
    print("✅ Weapon model loaded")
else:
    print("❌ Weapon model NOT FOUND")

# =========================
# TWILIO FUNCTION
# =========================
def send_sms(message):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=TWILIO_TO
        )
        print("📩 SMS sent")
    except Exception as e:
        print("❌ SMS failed:", e)

# =========================
# ALARM
# =========================
def play_alarm():
    winsound.Beep(2000, 800)
    winsound.Beep(2000, 800)

# =========================
# START CAMERA
# =========================
cap = cv2.VideoCapture(CAMERA_ID)
if not cap.isOpened():
    print("❌ Camera not opened")
    exit()

print("✅ Wild Vision Final System Started")
print("Press Q to exit")

last_alert_time = 0

# =========================
# MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    animal_found = False
    weapon_found = False
    animal_species = None

    # ---- PERSON + ANIMAL DETECTION ----
    detections = detect_model(frame, conf=CONF_DET, device=DEVICE, verbose=False)

    for r in detections:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = detect_model.names[cls_id]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # PERSON
            if label == "person":
                person_found = True
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, "PERSON", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # ANIMAL (single label only)
            elif label in ["dog","cat","horse","cow","sheep","elephant","bear","zebra","giraffe"]:
                animal_found = True

                animal_crop = frame[y1:y2, x1:x2]
                if animal_crop.size > 0:
                    cls_result = cls_model(animal_crop, conf=CONF_CLS, device=DEVICE, verbose=False)
                    animal_species = cls_result[0].names[int(cls_result[0].probs.top1)]

                display_name = animal_species.upper() if animal_species else "ANIMAL"

                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,200,0), 2)
                cv2.putText(frame, display_name, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,200,0), 2)

    # ---- WEAPON DETECTION (NO PERSON LABEL HERE) ----
    if weapon_model:
        weapons = weapon_model(frame, conf=0.5, device=DEVICE, verbose=False)
        for r in weapons:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                w_name = weapon_model.names[cls_id]

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                weapon_found = True

                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, f"WEAPON: {w_name.upper()}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    # ---- POACHING ALERT ----
    if person_found and weapon_found and animal_found and animal_species in PROTECTED_SPECIES:
        now = time.time()
        if now - last_alert_time > 10:
            last_alert_time = now

            alert_msg = (
                f"🚨 POACHING ALERT 🚨\n"
                f"Animal: {animal_species}\n"
                f"Time: {datetime.now()}"
            )

            print(alert_msg)
            play_alarm()
            send_sms(alert_msg)

    cv2.imshow("WILD VISION – FINAL SYSTEM", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
cap.release()
cv2.destroyAllWindows()
