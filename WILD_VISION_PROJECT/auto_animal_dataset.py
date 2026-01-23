import fiftyone as fo
import fiftyone.zoo as foz

dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=["Elephant", "Tiger", "Deer", "Bear"],
    max_samples=2000
)

dataset.export(
    export_dir="animal_dataset",
    dataset_type=fo.types.YOLOv5Dataset
)
