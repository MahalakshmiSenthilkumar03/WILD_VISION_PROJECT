import fiftyone as fo
import fiftyone.zoo as foz

# Load Open Images weapon-related classes
dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=["Gun", "Knife"],
    max_samples=1200
)

print("✅ Weapon dataset downloaded")

# Export to YOLO format
dataset.export(
    export_dir="datasets/weapon",
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="detections",
    classes=["Gun", "Knife"],
    split="train"
)

print("✅ Exported to YOLO format")
