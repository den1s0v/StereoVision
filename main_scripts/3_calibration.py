import os
import cv2
import numpy as np
import json
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration
from stereovision.exceptions import ChessboardNotFoundError

from user_settings import total_photos, img_height, img_width, rows, columns, square_size

# Global variables preset

PREVIEW_DETECTION_RESULTS = False

#### total_photos = 30

# Chessboard parameters
# Must use 6 Rows and 9 Column chessboard
#### rows = 6
#### columns = 9
#### square_size = 2.5

### image_size = (640, 360)
image_size = (img_width, img_height)

# This is the calibration class from the StereoVision package
calibrator = StereoCalibrator(rows, columns, square_size, image_size)
print('Start cycle')

# loop for the calibration. It will go through each pair of image one by one
for photo_counter in range(total_photos):
    print('Importing pair: ' + str(photo_counter))
    leftName = '../pairs/left_' + str(photo_counter).zfill(2) + '.png'
    rightName = '../pairs/right_' + str(photo_counter).zfill(2) + '.png'
    if os.path.isfile(leftName) and os.path.isfile(rightName):
        # reading the images in Color
        imgLeft = cv2.imread(leftName, 1)
        imgRight = cv2.imread(rightName, 1)

        # Ensuring both left and right images have the same dimensions
        (H, W, C) = imgLeft.shape

        imgRight = cv2.resize(imgRight, (W, H))

        # Calibrating the camera (getting the corners and drawing them)
        try:
            calibrator._get_corners(imgLeft)
            calibrator._get_corners(imgRight)
        except ChessboardNotFoundError as error:
            print(error)
            print("Pair No " + str(photo_counter) + " ignored")
        else:
            # add_corners function from the Class already helps us with cv2.imshow,
            # and hence we don't need to do it seperately
            ## definition: add_corners(self, image_pair, show_results=False)
            calibrator.add_corners((imgLeft, imgRight), show_results=PREVIEW_DETECTION_RESULTS)

    else:
        print("Pair not found")
        continue

print('Cycle Complete!')

#############
#############
#############

print('Starting calibration... It can take several minutes!')
calibration = calibrator.calibrate_cameras()
calibration.export('../calib_result')
print('Calibration complete!')

# Let's rectify and show last pair after  calibration
calibration = StereoCalibration(input_folder='../calib_result')
rectified_pair = calibration.rectify((imgLeft, imgRight))

cv2.imshow('Left Calibrated!', rectified_pair[0])
cv2.imshow('Right Calibrated!', rectified_pair[1])
# why save as jpg here and not png?
cv2.imwrite("../rectified_left.jpg", rectified_pair[0])
cv2.imwrite("../rectified_right.jpg", rectified_pair[1])
cv2.waitKey(0)
