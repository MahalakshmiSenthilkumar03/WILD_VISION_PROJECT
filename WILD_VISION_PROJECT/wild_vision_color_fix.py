import cv2
import winsound
from ultralytics import YOLO
from datetime import datetime

# ---------------- LOAD MODELS ----------------
detector = YOLO("yolov8n.pt")       # person + animal detection
classifier = YOLO("yolov8n-cls.pt") # exact animal species

# ---------------- SETTINGS ----------------
WEAPONS = ["knife", "gun", "rifle"]
PROTECTED_ANIMALS = ["elephant", "tiger", "lion", "rhino"]

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(0)
print("✅ Wild Vision Live Detection Started (Press Q to exit)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_detected = False
    animal_detected = False
    weapon_detected = False
    animal_name = "Unknown"

    results = detector(frame, conf=0.4)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = detector.names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # ---------------- PERSON ----------------
            if label == "person":
                person_detected = True
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "PERSON", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # ---------------- ANIMAL ----------------
            elif label in ["dog", "cat", "horse", "cow", "sheep", "elephant", "bear", "zebra", "giraffe"]:
                animal_detected = True

                crop = frame[y1:y2, x1:x2]
                if crop.size > 0:
                    cls_result = classifier(crop)
                    idx = cls_result[0].probs.top1
                    animal_name = cls_result[0].names[idx]

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"ANIMAL: {animal_name}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # ---------------- WEAPON ----------------
            elif label in WEAPONS:
                weapon_detected = True
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "WEAPON", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # ---------------- POACHING ALERT ----------------
    if person_detected and animal_detected and weapon_detected:
        zone = "Inner Forest" if animal_name.lower() in PROTECTED_ANIMALS else "Outer Forest"

        cv2.putText(frame,
                    f"🚨 POACHING DETECTED | {animal_name} | {zone}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    3)

        winsound.Beep(2000, 600)
        print(f"⚠ POACHING ALERT @ {datetime.now()}")

    cv2.imshow("Wild Vision - Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
