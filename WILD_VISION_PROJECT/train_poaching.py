from ultralytics import YOLO

def main():
    print("🚀 Training Anti-Poaching Model")

    model = YOLO("yolov8n.pt")

    model.train(
        data="poaching_data.yaml",
        epochs=40,
        imgsz=640,
        batch=8,
        device=0,
        workers=0  # IMPORTANT for Windows
    )

    print("✅ Training complete")

if __name__ == "__main__":
    main()
