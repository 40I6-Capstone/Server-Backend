import sys
sys.path.insert(1, '../')

from OpenCV.OpenCV import run_cv;
from PathPlanning import PathPlanning

import cv2
import matplotlib.pyplot as plt


img = cv2.imread("../OpenCV/Images/round.jpg");
shape = run_cv(img);
paths = PathPlanning();
print("planning path");
paths.planPath(shape, 20, 3, 5);
print("planed path");

print(shape.vertices);
plt.plot(shape.vertices[:,0], shape.vertices[:,1]);
plt.plot(shape.contour[:,0,0], shape.contour[:,0,1]);

for path in paths.paths:
    plt.plot(path.points[:,0], path.points[:,1]);

plt.show();