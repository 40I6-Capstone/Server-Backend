import cv2
import numpy as np

# Load the dictionary
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# Initialize the detector parameters
parameters = cv2.aruco.DetectorParameters_create()

# Initialize the video capture object
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video capture object
    ret, frame = cap.read()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the markers
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    # Draw the detected markers and show the image
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.imshow('Frame', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()