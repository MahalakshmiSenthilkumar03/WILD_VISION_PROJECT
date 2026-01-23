from ultralytics import YOLO
import cv2
import torch

# Load trained model
model = YOLO("runs/detect/train3/weights/best.pt")

# COCO class names (YOLO default)
CLASS_NAMES = model.names

print("✅ Model loaded on:", "GPU" if torch.cuda.is_available() else "CPU")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.4)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = CLASS_NAMES[cls_id]
            conf = box.conf[0]

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(
                frame,
                f"{label} {conf:.2f}",
                (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

    cv2.imshow("Wild Vision – Real-Time Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
