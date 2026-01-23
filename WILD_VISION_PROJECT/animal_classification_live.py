from ultralytics import YOLO
import cv2

# Load animal classification model
classifier = YOLO("yolov8n-cls.pt")

cap = cv2.VideoCapture(0)

print("✅ Animal classification started")
print("Press Q to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Classify full frame
    results = classifier(frame)

    probs = results[0].probs
    top1_id = probs.top1
    confidence = probs.top1conf
    animal_name = results[0].names[top1_id]

    label = f"{animal_name} ({confidence:.2f})"

    cv2.putText(
        frame,
        label,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Animal Species Classification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
