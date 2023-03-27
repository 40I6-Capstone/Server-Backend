import cv2
import time
import OpenCV
import numpy as np
import UAV.UAV as UAV

# Load the ArUco dictionary
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# Create the detector parameters
aruco_params = cv2.aruco.DetectorParameters_create()

# Set up the video capture device
# cap = cv2.VideoCapture(0)

# Create an empty list to store the marker IDs, positions and time since running
marker_list = []

# Get the start time
start_time = time.time()


def pixel_to_cm_ratio(aruco_x, aruco_y):
    # Use pixel mapping measurements to convert pixels to cm
    px = 960
    py = 720

    # Aruco marker real size is 10 x 10 cm
    ximage = px / aruco_x * 10
    yimage = py / aruco_y * 10

    # thetaX = 2*math.atan((ximage/2)/distance)
    # thetaY = 2*math.atan((yimage/2)/distance)

    rx = px / ximage  # pixels per cm
    ry = py / yimage  # pixels per cm
    return rx, ry;


while True:
    # Capture a frame from the video stream
    # ret, frame = cap.read()

    # receive frame from UAV photo
    frame = UAV.frame

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
            # currently, top-left of the image is 0,0

            # Compute the center of the marker by taking the average of the corner coordinates
            center = np.mean(marker_corners, axis=0)

            # Use pixel mapping to transform center coordinate:
            center[0] = center[0] * OpenCV.rx  # Transform x coordinate
            center[1] = center[1] * OpenCV.ry  # Transform y coordinate

            # Get the current time
            current_time = time.time() - start_time

            # Add the marker ID, position and time to the marker list
            marker_list.append((marker_id, center, current_time))

            # # Print the marker ID and its position
            # print("Marker ID: {}, Position: {}".format(marker_id, center))

            if marker_id == 1:  # USE MARKER 1 AS CALIBRATION FOR PIXEL MAPPING
                # Calculate the x and y dimensions of the marker in pixels
                x_dim = abs(marker_corners[0][0] - marker_corners[2][0])
                y_dim = abs(marker_corners[0][1] - marker_corners[2][1])
                rx, ry = pixel_to_cm_ratio(x_dim, y_dim)

    # Display the output frame
    cv2.imshow('output', frame)

    # Check for the 'q' key to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and close all windows
# cap.release()
cv2.destroyAllWindows()
