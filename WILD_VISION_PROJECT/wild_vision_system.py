import cv2
import time
import winsound
from ultralytics import YOLO

# ---------------- CONFIG ----------------
CAMERA_ID = 0
CONF = 0.4

WEAPON_MODEL_PATH = r"C:\AI\WILD_VISION_PROJECT\models\weapon.pt"

# ----------------------------------------

print("🔄 Loading models...")

# Person + animal detector (COCO)
main_model = YOLO("yolov8n.pt")

# Weapon model
weapon_model = None
try:
    weapon_model = YOLO(WEAPON_MODEL_PATH)
    print("✅ Weapon model loaded")
except:
    print("⚠ Weapon model NOT FOUND — weapon detection disabled")

print("✅ Wild Vision Live Detection Started")
print("Press Q to exit")

cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():
    print("❌ Camera not accessible")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_detected = False
    animal_detected = False
    weapon_detected = False

    # -------- MAIN DETECTION --------
    results = main_model(frame, conf=CONF, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = main_model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # PERSON
            if label == "person":
                person_detected = True
                color = (0, 255, 0)  # GREEN
                cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
                cv2.putText(frame, "PERSON", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # ANIMALS (basic COCO animals)
            elif label in ["elephant","bear","zebra","giraffe","dog","cat","cow","horse","sheep","deer"]:
                animal_detected = True
                color = (255, 200, 0)  # BLUE-YELLOW
                cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
                cv2.putText(frame, f"ANIMAL: {label.upper()}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # -------- WEAPON DETECTION --------
    if weapon_model:
        weapon_results = weapon_model(frame, conf=0.4, verbose=False)

        for r in weapon_results:
            for box in r.boxes:
                weapon_detected = True
                cls = int(box.cls[0])
                weapon_name = weapon_model.names[cls]

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, f"WEAPON: {weapon_name.upper()}",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    # -------- POACHING ALERT --------
    if person_detected and animal_detected and weapon_detected:
        cv2.putText(frame, "🚨 POACHING DETECTED 🚨",
                    (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0,0,255), 3)

        # ALARM
        winsound.Beep(2000, 700)

    # -------- DISPLAY --------
    cv2.imshow("Wild Vision - Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()
