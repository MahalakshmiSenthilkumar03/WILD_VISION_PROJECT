import fiftyone as fo
import fiftyone.zoo as foz

# Weapon classes available in Open Images
WEAPON_CLASSES = ["Gun", "Knife"]

print("⬇️ Downloading weapon dataset from Open Images...")

dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=WEAPON_CLASSES,
    max_samples=1000
)

print("✅ Dataset loaded")

# Filter samples that actually contain boxes
dataset = dataset.filter_labels(
    "ground_truth",
    fo.ViewField("label").is_in(WEAPON_CLASSES)
)

print(f"✅ Valid samples with weapons: {len(dataset)}")

# Export to YOLO format
dataset.export(
    export_dir="datasets/weapon",
    dataset_type=fo.types.YOLOv5Dataset,
    label_field="ground_truth",
    classes=WEAPON_CLASSES
)

print("✅ Weapon dataset exported to YOLO format")
