from ultralytics import YOLO
import cv2
import datetime
import os
import requests

# =========================
# LOAD MODELS (AUTO STREAM)
# =========================
detect_model = YOLO("yolov8m.pt")        # Detection
classify_model = YOLO("yolov8m-cls.pt")  # Classification

# =========================
# SETTINGS
# =========================
ALERT_DIR = "poaching_alerts"
os.makedirs(ALERT_DIR, exist_ok=True)

ANIMALS_OF_INTEREST = [
    "elephant", "tiger", "leopard", "deer",
    "bear", "boar", "buffalo", "lion"
]

WEAPONS = ["knife", "gun"]
HUMAN = "person"

# =========================
# GEO LOCATION (IP BASED)
# =========================
def get_location():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=3).json()
        return f"{r.get('city')}, {r.get('region')}, {r.get('country')}"
    except:
        return "Unknown Location"

# =========================
# CAMERA
# =========================
cap = cv2.VideoCapture(0)

print("🚀 Wild Vision Anti-Poaching System Started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detected_labels = set()

    # -------------------------
    # DETECTION
    # -------------------------
    results = detect_model(frame, conf=0.4, device=0, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = r.names[cls]
            detected_labels.add(label)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            color = (0, 255, 0)

            if label in WEAPONS:
                color = (0, 0, 255)
            elif label == HUMAN:
                color = (255, 255, 0)

            cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
            cv2.putText(frame, label, (x1, y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # -------------------------
    # CLASSIFICATION (ANIMALS)
    # -------------------------
    cls_result = classify_model(frame, device=0, verbose=False)[0]
    animal_name = cls_result.names[cls_result.probs.top1]
    animal_conf = cls_result.probs.top1conf

    if animal_conf > 0.5:
        cv2.putText(frame,
                    f"Animal: {animal_name} ({animal_conf:.2f})",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2)

    # -------------------------
    # POACHING LOGIC
    # -------------------------
    if HUMAN in detected_labels and detected_labels.intersection(WEAPONS):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        location = get_location()

        alert_text = "🚨 POACHING ALERT"
        cv2.putText(frame, alert_text, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 3)

        # Save evidence
        img_path = f"{ALERT_DIR}/alert_{timestamp}.jpg"
        cv2.imwrite(img_path, frame)

        print(f"""
🚨 POACHING DETECTED
Time: {timestamp}
Animal: {animal_name}
Location: {location}
Evidence Saved: {img_path}
""")

    # -------------------------
    # DISPLAY
    # -------------------------
    cv2.imshow("Wild Vision – Anti-Poaching", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
