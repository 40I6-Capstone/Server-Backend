import cv2
import numpy as np

# Load the ArUco dictionary
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# Create the detector parameters
aruco_params = cv2.aruco.DetectorParameters_create()

# Start the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the ArUco markers in the frame
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    # If any markers are detected, draw the markers and their IDs on the frame
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Loop over the detected markers
        for i, marker_id in enumerate(ids):
            # Get the corner coordinates of the marker
            marker_corners = corners[i][0]

            # Compute the center of the marker by taking the average of the corner coordinates
            center = np.mean(marker_corners, axis=0)

            # Print the marker ID and its position
            print("Marker ID: {}, Position: {}".format(marker_id, center))

    # Display the output frame
    cv2.imshow('output', frame)

    # Wait for the 'q' key to be pressed to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
