import cv2
import torch
from ultralytics import YOLO

# -----------------------------
# DEVICE (GPU if available)
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# -----------------------------
# LOAD MODELS
# -----------------------------
print("Loading models...")

person_animal_model = YOLO("yolov8n.pt").to(device)     # detection
animal_cls_model = YOLO("yolov8m-cls.pt").to(device)    # species classification

print("Models loaded successfully")

# -----------------------------
# VIDEO CAPTURE
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Camera not opened")

print("Camera started. Press Q to exit.")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO DETECTION
    results = person_animal_model(frame, conf=0.4, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = person_animal_model.names[cls_id]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # -----------------------------
            # PERSON (ONLY ONE LABEL)
            # -----------------------------
            if label == "person":
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(
                    frame,
                    "PERSON",
                    (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,255,0),
                    2
                )

            # -----------------------------
            # ANIMAL → SPECIES CLASSIFIER
            # -----------------------------
            elif label in ["dog","cat","horse","cow","sheep","bird"]:
                crop = frame[y1:y2, x1:x2]

                if crop.size == 0:
                    continue

                cls_result = animal_cls_model(crop, verbose=False)[0]
                species_id = int(cls_result.probs.top1)
                species_name = cls_result.names[species_id].upper()

                cv2.rectangle(frame, (x1,y1), (x2,y2), (255,200,0), 2)
                cv2.putText(
                    frame,
                    species_name,
                    (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255,200,0),
                    2
                )

    cv2.imshow("Wild Vision – Species Accurate", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
print("Stopped cleanly")
