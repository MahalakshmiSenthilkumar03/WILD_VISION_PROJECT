from ultralytics import YOLO
import cv2

print("📸 Starting real-time image classification")

# Load pretrained YOLO classifier
model = YOLO("yolov8n-cls.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Webcam not detected")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run classification
    results = model(frame)

    label = results[0].names[results[0].probs.top1]
    conf = results[0].probs.top1conf

    # Display result
    cv2.putText(
        frame,
        f"{label} ({conf:.2f})",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    cv2.imshow("Real-Time Image Classification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
