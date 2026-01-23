import cv2
import numpy as np

print("OpenCV version:", cv2.__version__)

# Create a dummy image (black image)
img = np.zeros((480, 640, 3), dtype=np.uint8)

cv2.putText(
    img,
    "OPENCV WINDOW WORKS",
    (50, 240),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)

cv2.imshow("TEST WINDOW", img)
cv2.waitKey(2000)
cv2.destroyAllWindows()
