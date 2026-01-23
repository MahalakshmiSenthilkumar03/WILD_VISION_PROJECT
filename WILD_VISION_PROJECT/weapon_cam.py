import cv2
import os
from ultralytics import YOLO

# ===============================
# CONFIG
# ===============================
WEAPON_MODEL_PATH = r"C:\AI\WILD_VISION_PROJECT\models\weapon.pt"
CAMERA_ID = 0
CONFIDENCE = 0.4
# ===============================

print("🔄 Starting Weapon Detection Test")

# ---- Check model file
if not os.path.exists(WEAPON_MODEL_PATH):
    print("❌ weapon.pt NOT FOUND at:", WEAPON_MODEL_PATH)
    exit()

print("✅ weapon.pt found")

# ---- Load weapon model
try:
    weapon_model = YOLO(WEAPON_MODEL_PATH)
    print("✅ Weapon model loaded successfully")
except Exception as e:
    print("❌ Failed to load weapon model")
    print(e)
    exit()

# ---- Open camera
cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Camera not opening")
    exit()

print("📷 Camera opened")
print("Press Q to exit")

# ---- Loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame not received")
        break

    # ---- Run weapon detection
    results = weapon_model(frame, conf=CONFIDENCE, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = weapon_model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # RED box for weapon
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
            cv2.putText(
                frame,
                f"WEAPON: {label.upper()}",
                (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,0,255),
                2
            )

    cv2.imshow("Weapon Detection Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("🛑 Stopped")
