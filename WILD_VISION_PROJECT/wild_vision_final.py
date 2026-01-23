import cv2
import torch
import winsound
from ultralytics import YOLO

# ================= CONFIG =================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CONF = 0.4

print("Using device:", DEVICE)

# ================= LOAD MODELS =================
print("Loading models...")
detector = YOLO("yolov8m.pt").to(DEVICE)        # detection only
classifier = YOLO("yolov8m-cls.pt").to(DEVICE)  # species classification
print("Models loaded")

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Camera not accessible")

print("Live detection started (Press Q to exit)")

# ================= MAIN LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    animal_found = False
    weapon_found = False
    animal_name = ""

    results = detector(frame, conf=CONF, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = detector.names[cls_id]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # ---------- PERSON ----------
            if label == "person":
                person_found = True
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, "Person", (x1, y1-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # ---------- ANIMAL ----------
            elif label in ["dog","cat","horse","sheep","cow","elephant","bear","zebra","giraffe"]:
                animal_found = True
                crop = frame[y1:y2, x1:x2]

                if crop.size > 0:
                    cls_res = classifier(crop, verbose=False)[0]
                    animal_name = classifier.names[int(cls_res.probs.top1)]

                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,165,0), 2)
                cv2.putText(frame, animal_name, (x1, y1-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,165,0), 2)

            # ---------- WEAPON ----------
            elif label in ["knife", "gun"]:
                weapon_found = True
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)
                cv2.putText(frame, label.upper(), (x1, y1-8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    # ---------- POACHING ALERT ----------
    if person_found and animal_found and weapon_found:
        winsound.Beep(2000, 600)
        cv2.putText(frame, "⚠ POACHING DETECTED ⚠",
                    (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

    cv2.imshow("Wild Vision – Final", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
