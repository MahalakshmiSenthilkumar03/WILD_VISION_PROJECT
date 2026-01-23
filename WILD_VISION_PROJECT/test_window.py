import cv2
import numpy as np

img = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.putText(img, "WINDOW TEST OK", (80,200),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

cv2.imshow("TEST WINDOW", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
