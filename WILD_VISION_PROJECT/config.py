# ===============================
# Wild Vision System Configuration
# ===============================

# Webcam index
CAMERA_ID = 0   # 0 = default laptop camera

# Camera metadata
CAMERA_NUMBER = "CAM-01"
CAMERA_LOCATION = {
    "area": "Forest Zone A",
    "range": "Inner Forest",
    "latitude": 11.0168,
    "longitude": 76.9558
}

# Detection thresholds
PERSON_CONFIDENCE = 0.45
ANIMAL_CONFIDENCE = 0.45
WEAPON_CONFIDENCE = 0.40

# Alert settings
ENABLE_SOUND_ALERT = True
ENABLE_IMAGE_CAPTURE = True

# Storage paths
ALERT_IMAGE_DIR = "alerts"
LOG_FILE = "logs.json"
