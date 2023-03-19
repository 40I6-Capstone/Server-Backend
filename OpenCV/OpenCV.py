#  Author: Julian Morrone, morronej@mcmaster.ca
#  This code uses the Python OpenCV library to isolate an oil spill from the surrounding water via photos that will be passed in
#  It then draws a bounding box around the spill, adds a buffer and creates a discretized circle around it that can be followed by the UGV's to place Bouy's and contain the spill

import cv2
import numpy as np
import math

global debug
debug = False

# Set Pipeline to True to see image pipeline
global Pipeline
Pipeline = True


cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)
cv2.namedWindow('Contour', cv2.WINDOW_NORMAL)

if Pipeline:
    cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
    cv2.namedWindow('mask_result', cv2.WINDOW_NORMAL)
    cv2.namedWindow('Edge', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('High Contrast', cv2.WINDOW_NORMAL)


# try increasing contrast and/or inverting colors to help bounding - don't see much of a difference
# use contours method to select largest shape from mask result - increase lieniency
# don't blur the image to take care of the high spots
# also worth trying: as part of setup, take easier images with better lighting
# do the contour and edge on the mask, not the mask result - can use blur on the mask as well

# another potential idea is to make the whole image either black or white based on how close the pixel is to that colour then select the shape from there

def apply_brightness_contrast(input_img, brightness=0, contrast=0):  # function to change brightness and contrast in the image
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def nothing(x):
    pass


# takes four arguments: the x and y coordinates of the center of the circle, the radius of the circle, and the side length. The function uses the math module to calculate the x and y coordinates of each vertex of the polygon,
# and appends these coordinates to a list called points. The function then returns this list of points.
# effectively, this returns the center point for each oil boom in a list.
#TODO - How will we ensure the UGV places the boom at the appropriate angle?
def circle_discretize(center_x, center_y, radius, side_len):
    num_sides = math.ceil(math.pi / (math.atan(side_len / (2 * radius))))  # formula derived on onenote
    points = []
    for i in range(num_sides):
        angle = 2 * math.pi * i / num_sides
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    return points

def run_cv(frame: cv2.Mat):
    if debug:
        cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)

        # create trackbars to edit HSV lower and upper values for the mask
        # also create trackbars to play with canny upper and lower thresholds
        cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
        cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
        cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
        cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)
        cv2.createTrackbar('Canny Lower', 'Trackbars', 0, 255, nothing)
        cv2.createTrackbar('Canny Upper', 'Trackbars', 0, 255, nothing)

    # while True:
    # _, frame = cap.read()
    # frame = 
    frame_high_contrast = apply_brightness_contrast(frame, 0, 20)
    hsv = cv2.cvtColor(frame_high_contrast, cv2.COLOR_BGR2HSV)

    # min = [0,0,0]
    # max = [180,255,255]

    # Get Lower and Upper HSV+Canny values from the trackbars
    if debug:
        l_h = cv2.getTrackbarPos("L - H", "Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "Trackbars")
        canny_lower = cv2.getTrackbarPos("Canny Lower", "Trackbars")
        canny_upper = cv2.getTrackbarPos("Canny Upper", "Trackbars")
    else:
        l_h = 30
        l_s = 0
        l_v = 0
        u_h = 179
        u_s = 255
        u_v = 255
        canny_lower = 0
        canny_upper = 0

    lower = np.array([l_h, l_s, l_v])
    upper = np.array([u_h, u_s, u_v])

    # Mask is applied to hsv of orignal image, using values selected on the trackbar
    mask = cv2.inRange(hsv, lower, upper)
    invert_mask = cv2.bitwise_not(mask)  # inverted version of the mask

    # mask result (selecting only the oil spill from the original image)
    result = cv2.bitwise_and(frame, frame, mask=invert_mask)

    # apply a Gaussian Blur to make the contours easier to detect
    img_blur = cv2.GaussianBlur(result, (17, 17), 0)
    edge = cv2.Canny(img_blur, canny_lower, canny_upper, L2gradient=True)

    # find the contours in the inverted mask
    contours, _ = cv2.findContours(invert_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img_copy = frame.copy()

    # Find the largest Contour and draw a bounding box
    try:
        # find the biggest countour (c) by the area
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)  # (x,y) is the top-left coordinate of the rectangle and (w,h) is its width and height.

        # red color in BGR
        red = (0, 0, 255)
        blue = (255, 0, 0)
        green = (0, 0, 255)
        orange = (0, 123, 255)
        pink = (165, 0, 255)

        # draw the bounding rectangle for the biggest contour (c) in red
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), red, 15)

        # Find the index of the largest contour
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]

        # # draw the largest contour in blue
        cv2.drawContours(img_copy, contours, max_index, blue, 15)

        # add a buffer to the bounding box
        largest_side = max(w, h)
        buffer = 1.1
        largest_side = largest_side * buffer

        # Draw a circle around the spill based on the buffer bounding box. We must round to get a whole number of pixels otherwise drawing the circle will not work
        center = (round(x + w / 2), round(y + h / 2))
        radius = round(largest_side / 2)
        color = orange
        thickness = 15
        cv2.circle(img_copy, center, radius, color, thickness)

        # calculate the midpoints of each boom when placed in the discretized circle
        # TODO - modify side length in this function once we know the true length of the booms we will be using
        circle_coords = circle_discretize(center_x=round(x + w / 2), center_y=round(y + h / 2), radius=radius, side_len=200)
        # circle_coords = get_all_circle_coords(x_center=round(x + w / 2),
        #                                       y_center=round(y + h / 2),
        #                                       radius=radius,
        #                                       n_points=15)

        # Convert the coordinates to integers so that they can actually be displayed on the image
        int_circle_coords = list(np.rint(np.array(circle_coords)).astype(int))

        origin = [round(x + w / 2), round(y + h / 2)]
        unit_normal = []
        # Draw all the points on the image &
        # Calculate a vector between all the points and the origin of the bounding circle and normalize them
        for i in range(len(int_circle_coords)):
            cv2.circle(img_copy, (int_circle_coords[i][0], int_circle_coords[i][1]), radius=15, color=pink, thickness=-1)
            point = (int_circle_coords[i][0], int_circle_coords[i][1]) # each midpoint on the discretized circle
            vector = np.subtract(origin, point)  # To find the directional vector, subtract the coordinates of the initial point from the coordinates of the terminal point.
            unit_normal.append(vector / np.linalg.norm(vector))



    except:  # Prevents code from crashing when upper and lower limits are all set to 0 (i.e. trackbars not modified)
        print("no contour found")

    # draw the contours on a copy of the original image
    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 3)

    # Display
    cv2.imshow("Original Image", frame)
    cv2.imshow("Contour", img_copy)
    if Pipeline:
        frame_high_contrast = cv2.resize(frame_high_contrast,(350,350), interpolation = cv2.INTER_AREA)
        mask = cv2.resize(mask, (350, 350), interpolation=cv2.INTER_AREA)
        result = cv2.resize(result, (350, 350), interpolation=cv2.INTER_AREA)
        edge = cv2.resize(edge, (350, 350), interpolation=cv2.INTER_AREA)

        cv2.imshow("High Contrast", frame_high_contrast)
        cv2.imshow("mask", mask)
        cv2.imshow("mask_result", result)
        cv2.imshow('Edge', edge)
        #canvas[60:60+mask.shape[0],200:200 + mask.shape[1]] = mask
    cv2.waitKey(10000)
    cv2.destroyAllWindows()
    return circle_coords;

        # # wait for a key to pressed, if not then close
        # key = cv2.waitKey(1)
        # if key == 27:
        #     break
