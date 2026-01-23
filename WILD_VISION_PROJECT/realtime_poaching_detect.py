from ultralytics import YOLO
import cv2, os, json
from datetime import datetime

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)

os.makedirs("alerts/images", exist_ok=True)
EVENT_FILE = "alerts/events.json"

if not os.path.exists(EVENT_FILE):
    with open(EVENT_FILE, "w") as f:
        json.dump([], f)

def log_event(image_path, labels):
    event = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "Forest Zone A (Demo)",
        "labels": list(labels),
        "image": image_path
    }
    with open(EVENT_FILE, "r+") as f:
        data = json.load(f)
        data.append(event)
        f.seek(0)
        json.dump(data, f, indent=4)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.4)
    detected = set()

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            detected.add(label)

            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,label,(x1,y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

    # 🚨 POACHING LOGIC
    if "person" in detected and any(a in detected for a in ["elephant","deer","dog","cat"]):
        fname = f"alerts/images/poaching_{int(datetime.now().timestamp())}.jpg"
        cv2.imwrite(fname, frame)
        log_event(fname, detected)

        cv2.putText(frame,"🚨 POACHING ALERT",(30,50),
                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

    cv2.imshow("Wild Vision – Live", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
