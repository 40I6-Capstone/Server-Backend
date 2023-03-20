from OpenCV import run_cv
import cv2
import matplotlib.pyplot as plt
import numpy as np;

img = cv2.imread("./Images/round.jpg");
[points, contour] = run_cv(img);
npPoints = np.array(points);
print(contour);
plt.plot(npPoints[:,0], npPoints[:,1]);
plt.plot(contour[:,0,0], contour[:,0,1]);
plt.show();