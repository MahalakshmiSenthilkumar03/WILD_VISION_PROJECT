from ultralytics import YOLO
import cv2
import datetime
import os
import json

# Models
detect_model = YOLO("yolov8m.pt")
classify_model = YOLO("yolov8m-cls.pt")

ALERT_DIR = "poaching_alerts"
os.makedirs(ALERT_DIR, exist_ok=True)

ALERT_LOG = os.path.join(ALERT_DIR, "alerts.json")
if not os.path.exists(ALERT_LOG):
    with open(ALERT_LOG, "w") as f:
        json.dump([], f)

def generate_frames():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected = set()

        # Detection
        results = detect_model(frame, conf=0.4, device=0, verbose=False)
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = r.names[cls]
                detected.add(label)

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(frame, label, (x1,y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # Classification
        cls_res = classify_model(frame, device=0, verbose=False)[0]
        animal = cls_res.names[cls_res.probs.top1]

        cv2.putText(frame, f"Animal: {animal}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)

        # Poaching condition
        if "person" in detected and ("knife" in detected or "gun" in detected):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img_name = f"alert_{int(datetime.datetime.now().timestamp())}.jpg"
            img_path = os.path.join(ALERT_DIR, img_name)
            cv2.imwrite(img_path, frame)

            with open(ALERT_LOG, "r+") as f:
                data = json.load(f)
                data.append({
                    "time": timestamp,
                    "animal": animal,
                    "image": img_name
                })
                f.seek(0)
                json.dump(data, f, indent=2)

            cv2.putText(frame, "🚨 POACHING ALERT",
                        (20,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

        # Stream frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
