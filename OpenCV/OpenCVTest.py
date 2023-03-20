from OpenCV import (run_cv);
import cv2
import matplotlib.pyplot as plt
import numpy as np;

img = cv2.imread("./Images/round.jpg");
shape = run_cv(img);
print(shape.vertices);
plt.plot(shape.vertices[:,0], shape.vertices[:,1]);
plt.plot(shape.contour[:,0,0], shape.contour[:,0,1]);
plt.show();