from ultralytics import YOLO

print("🚀 Starting Wild Vision Training...")

# Load pretrained YOLOv8 model
model = YOLO("yolov8n.pt")

# Train with auto-downloaded dataset
model.train(
    data="wild_data.yaml",
    epochs=10,
    imgsz=640,
    batch=8,
    device=0,          # GPU
    workers=2,
    project="runs",
    name="wild_vision"
)

print("✅ Training finished successfully")
