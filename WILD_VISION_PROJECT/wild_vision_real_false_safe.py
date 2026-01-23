import cv2
import time
import requests
from ultralytics import YOLO

# ===================== CONFIG =====================
PERSON_CLASS = "person"
CONF_THRESH = 0.5
REAL_FRAMES_REQUIRED = 5

BACKEND_URL = "http://localhost:5000/api/poaching"

ZONE = "Zone-A"
CAMERA_ID = "CAM-01"

# ===================== MODELS =====================
print("🔄 Loading models...")
detector = YOLO("yolov8n.pt")              # person + animal
weapon_model = YOLO("models/weapon.pt")   # weapon only
print("✅ Weapon model loaded")

# ===================== STATE =====================
real_counter = 0
last_alert_time = 0
ALERT_COOLDOWN = 10  # seconds

# ===================== HELPERS =====================
def send_real_alert(animal, weapon, confidence):
    payload = {
        "animal": animal,
        "weapon": weapon,
        "zone": ZONE,
        "camera": CAMERA_ID,
        "confidence": confidence
    }
    requests.post(BACKEND_URL, json=payload)
    print("🚨 REAL POACHING ALERT SENT")

# ===================== MAIN LOOP =====================
cap = cv2.VideoCapture(0)
print("✅ Wild Vision Started (Press Q to exit)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ------------------ DETECTION ------------------
    det_results = detector(frame, conf=CONF_THRESH, verbose=False)[0]
    weapon_results = weapon_model(frame, conf=CONF_THRESH, verbose=False)[0]

    persons = []
    animals = []
    weapons = []

    # ---- PERSON & ANIMAL ----
    for box in det_results.boxes:
        cls = int(box.cls[0])
        label = detector.names[cls]

        if label == PERSON_CLASS:
            persons.append(box)
        elif label not in ["car", "chair", "truck"]:  # ignore junk
            animals.append(label)

    # ---- WEAPON ----
    for box in weapon_results.boxes:
        cls = int(box.cls[0])
        weapons.append(weapon_model.names[cls])

    # ================= REAL POACHING RULE =================
    if persons and animals and weapons:
        real_counter += 1
    else:
        real_counter = 0

    # ---- CONFIRM REAL ALERT ----
    if real_counter >= REAL_FRAMES_REQUIRED:
        now = time.time()
        if now - last_alert_time > ALERT_COOLDOWN:
            send_real_alert(
                animal=animals[0],
                weapon=weapons[0],
                confidence=0.9
            )
            last_alert_time = now
            real_counter = 0

    # ================= FALSE ALERT ENGINE =================
    # ❗ DOES NOT BLOCK REAL ALERT ❗
    false_alert = None

    if persons and animals and not weapons:
        false_alert = "Tourist / Forest Staff"
    elif weapons and not animals:
        false_alert = "Weapon Carry (Non-poaching)"
    elif persons and not animals and not weapons:
        false_alert = None  # ignored
    elif animals and not persons:
        false_alert = None  # ignored

    if false_alert:
        print("⚠ False Alert:", false_alert)

    # ================= VISUAL =================
    for box in persons:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        cv2.putText(frame, "PERSON", (x1,y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    for a in animals:
        cv2.putText(frame, a.upper(), (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,200,0), 2)

    for w in weapons:
        cv2.putText(frame, w.upper(), (20,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("Wild Vision - Real Safe Mode", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
