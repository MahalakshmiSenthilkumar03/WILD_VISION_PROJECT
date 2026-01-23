import cv2
import time
import torch
import winsound
from ultralytics import YOLO
from twilio.rest import Client
from datetime import datetime

# ================= CONFIG =================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PERSON_MODEL = "yolov8n.pt"
ANIMAL_MODEL = "yolov8n.pt"
WEAPON_MODEL = r"C:\AI\WILD_VISION_PROJECT\models\weapon.pt"
SPECIES_MODEL = "yolov8n-cls.pt"

PROTECTED_SPECIES = ["lion", "tiger", "elephant", "leopard"]

# ---- Twilio ----
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"
TWILIO_FROM = "+1XXXXXXXXXX"
TWILIO_TO = "+91XXXXXXXXXX"

SMS_COOLDOWN = 30  # seconds
last_sms_time = 0

# ==========================================

print("🔄 Loading models...")
person_model = YOLO(PERSON_MODEL).to(DEVICE)
animal_model = YOLO(ANIMAL_MODEL).to(DEVICE)
species_model = YOLO(SPECIES_MODEL).to(DEVICE)

weapon_model = None
if cv2.haveImageReader(WEAPON_MODEL):
    weapon_model = YOLO(WEAPON_MODEL).to(DEVICE)
    print("✅ Weapon model loaded")
else:
    print("❌ Weapon model missing")

client = Client(TWILIO_SID, TWILIO_TOKEN)

# ==========================================

def send_sms_once(msg):
    global last_sms_time
    now = time.time()
    if now - last_sms_time > SMS_COOLDOWN:
        client.messages.create(body=msg, from_=TWILIO_FROM, to=TWILIO_TO)
        last_sms_time = now
        print("📨 SMS SENT")

def alarm():
    winsound.Beep(2000, 800)

# ==========================================

cap = cv2.VideoCapture(0)
print("✅ Wild Vision Started (Press Q to exit)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    person_found = False
    animal_found = False
    weapon_found = False
    animal_species = None

    # ---------------- PERSON DETECTION ----------------
    persons = person_model(frame, conf=0.4, verbose=False)[0]
    for box in persons.boxes:
        cls = int(box.cls[0])
        if persons.names[cls] == "person":
            person_found = True
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,"PERSON",(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

            # -------- WEAPON DETECTION (ONLY INSIDE PERSON) --------
            if weapon_model:
                person_crop = frame[y1:y2, x1:x2]
                weapons = weapon_model(person_crop, conf=0.45, verbose=False)[0]
                for wbox in weapons.boxes:
                    weapon_found = True
                    wx1,wy1,wx2,wy2 = map(int, wbox.xyxy[0])
                    cv2.rectangle(
                        frame,
                        (x1+wx1,y1+wy1),
                        (x1+wx2,y1+wy2),
                        (0,0,255),2
                    )
                    cv2.putText(frame,"WEAPON",
                        (x1+wx1,y1+wy1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)

    # ---------------- ANIMAL + SPECIES ----------------
    animals = animal_model(frame, conf=0.4, verbose=False)[0]
    for box in animals.boxes:
        cls = int(box.cls[0])
        name = animals.names[cls]
        if name in ["dog","cat","horse","cow","sheep","elephant","bear","zebra","giraffe"]:
            animal_found = True
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            crop = frame[y1:y2, x1:x2]

            sp = species_model(crop, verbose=False)[0]
            animal_species = sp.names[int(sp.probs.top1)]

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,165,0),2)
            cv2.putText(frame,animal_species.upper(),
                (x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,165,0),2)

    # ---------------- POACHING LOGIC ----------------
    if person_found and weapon_found and animal_found and animal_species in PROTECTED_SPECIES:
        alarm()
        msg = f"🚨 POACHING ALERT\nAnimal: {animal_species}\nTime: {datetime.now()}"
        send_sms_once(msg)
        cv2.putText(frame,"POACHING DETECTED",
            (50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

    cv2.imshow("WILD VISION - FINAL", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
