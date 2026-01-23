import os

LABELS_DIR = r"C:\AI\WILD_VISION_PROJECT\datasets\weapon\labels"
PERSON_CLASS_ID = "2"   # change ONLY if your person class id is different

removed = 0
checked = 0

for root, _, files in os.walk(LABELS_DIR):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)
            with open(path, "r") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                if not line.startswith(PERSON_CLASS_ID + " "):
                    new_lines.append(line)
                else:
                    removed += 1

            with open(path, "w") as f:
                f.writelines(new_lines)

            checked += 1

print(f"Checked {checked} label files")
print(f"Removed {removed} person annotations")
print("Weapon dataset cleaned successfully")
