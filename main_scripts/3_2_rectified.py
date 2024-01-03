""" Rectify all images within `dir_input` and save the results to `dir_output`. """

import os

import cv2
from stereovision.calibration import StereoCalibration

from user_settings import total_photos, img_height, img_width


image_size = (img_width, img_height)

# dir_input = "../pairs"
dir_input = "../good__pairs"
dir_output = "../rectified_pairs"


# This is the calibration class from the StereoVision package
calibration = StereoCalibration(input_folder='../calib_result')

if not os.path.isdir(dir_output):
    os.makedirs(dir_output)


# loop for the calibration. It will go through each pair of image one by one
for photo_counter in range(total_photos):
    print('Importing pair: ' + str(photo_counter))
    leftName = os.path.join(dir_input, 'left_' + str(photo_counter).zfill(2) + '.png')
    rightName = os.path.join(dir_input, 'right_' + str(photo_counter).zfill(2) + '.png')
    if os.path.isfile(leftName) and os.path.isfile(rightName):
        # reading the images in Color
        imgLeft = cv2.imread(leftName, 1)
        imgRight = cv2.imread(rightName, 1)

        # Ensuring both left and right images have the same dimensions
        (H, W, C) = imgLeft.shape

        imgRight = cv2.resize(imgRight, (W, H))

        # Let's rectify and show last pair after  calibration
        rectified_pair = calibration.rectify((imgLeft, imgRight))

        leftName = os.path.join(dir_output, 'left_' + str(photo_counter).zfill(2) + '.png')
        rightName = os.path.join(dir_output, 'right_' + str(photo_counter).zfill(2) + '.png')
        cv2.imwrite(leftName, rectified_pair[0])
        cv2.imwrite(rightName, rectified_pair[1])

    else:
        print("Pair not found")
        continue


print('Cycle Complete!')
