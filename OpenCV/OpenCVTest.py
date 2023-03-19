from OpenCV import run_cv
import cv2

img = cv2.imread("./Images/round.jpg");
points = run_cv(img);
print(points);