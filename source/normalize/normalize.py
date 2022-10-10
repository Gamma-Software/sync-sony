import cv2
import numpy as np

image = cv2.imread("image.jpg")
image_norm = cv2.normalize(image, None, 25, 255, cv2.NORM_MINMAX)
cv2.imwrite("image_norm.jpg", image_norm)