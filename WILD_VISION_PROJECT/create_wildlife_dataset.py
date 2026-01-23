import fiftyone as fo
import fiftyone.zoo as foz
import os

EXPORT_DIR = "datasets/wildlife"
LABEL_FIELD = "ground_truth"

CLASSES = [
    "Elephant",
    "Tiger",
    "Lion",
    "Deer",
    "Bear",
    "Person"
]

os.makedirs(EXPORT_DIR, exist_ok=True)

dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=CLASSES,
    max_samples=1500
)

print("✅ Dataset loaded")

dataset = dataset.filter_labels(
    LABEL_FIELD,
    fo.ViewField("confidence") > 0
)

print(f"✅ Valid labeled samples: {len(dataset)}")

dataset.export(
    export_dir=EXPORT_DIR,
    dataset_type=fo.types.YOLOv5Dataset,
    label_field=LABEL_FIELD,
    split="train",
    classes=CLASSES
)

print("✅ YOLO wildlife dataset exported")
