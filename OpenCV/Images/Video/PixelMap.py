import cv2
import numpy as np

# Load the image
img = cv2.imread('pixleMap20cm.jpeg')

# Convert the image to HSV color space
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define the range of yellow color in HSV
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

# Threshold the HSV image to get only yellow colors
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

# Apply a Gaussian blur to the mask to reduce noise
blurred_mask = cv2.GaussianBlur(mask, (5, 5), 0)

# Detect edges in the mask using the Canny algorithm
edges = cv2.Canny(blurred_mask, 50, 150)

# Find contours in the mask
contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Loop over the contours
for cnt in contours:
    # Approximate the contour to a polygon
    approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

    # Check if the polygon has 4 sides (a square)
    if len(approx) == 4:
        # Draw a green rectangle around the square
        cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)

# Display the image
cv2.imshow("Image with Yellow Square Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
