import fiftyone as fo
import fiftyone.zoo as foz
import os
import shutil

DATASET_DIR = "datasets"

CLASSES = [
    "Person",
    "Gun",
    "Knife",
    "Elephant",
    "Deer",
    "Tiger",
    "Leopard",
    "Wild boar"
]

YOLO_CLASSES = {
    "Person": 0,
    "Gun": 1,
    "Knife": 2,
    "Elephant": 3,
    "Deer": 4,
    "Tiger": 5,
    "Leopard": 6,
    "Wild boar": 7
}

print("⬇️ Loading OpenImages dataset...")
dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=CLASSES,
    max_samples=3000,
)

print("🔍 Keeping only samples with bounding boxes...")
dataset = dataset.match(
    fo.ViewField("detections.detections").length() > 0
)

print("📤 Exporting to YOLO format...")
dataset.export(
    export_dir=DATASET_DIR,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="detections",
    classes=list(YOLO_CLASSES.keys()),
)

print("✅ Dataset ready in 'datasets/'")
