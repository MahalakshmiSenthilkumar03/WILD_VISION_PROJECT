from ultralytics import YOLO
import cv2

model = YOLO("yolov8n-cls.pt")  # pretrained classifier

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    top1 = results[0].names[results[0].probs.top1]
    conf = results[0].probs.top1conf

    cv2.putText(
        frame,
        f"{top1} {conf:.2f}",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,0,255),
        3
    )

    cv2.imshow("Real-Time Image Classification", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
