from ultralytics import YOLO

def main():
    print("🚀 Starting Wild Vision model training")

    model = YOLO("yolov8n.pt")

    model.train(
        data="coco128.yaml",
        epochs=5,
        imgsz=640,
        batch=8,
        device=0,
        workers=0   # 🔴 VERY IMPORTANT FOR WINDOWS
    )

    print("✅ Training completed successfully")

if __name__ == "__main__":
    main()
