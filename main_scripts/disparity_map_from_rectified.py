"""
Source: https://www.opencvhelp.org/tutorials/advanced/stereo-vision/


"""

import os


# Step 1: Install OpenCV and Other Dependencies
# First, let’s install OpenCV and other required libraries:
#
# pip install opencv-python opencv-python-headless numpy

import cv2


# Step 2: Load Rectified Images
# We’ll start by loading the rectified images using OpenCV:

dir_input = "../rectified_pairs"
photo_counter = 8

leftName = os.path.join(dir_input, 'left_' + str(photo_counter).zfill(2) + '.png')
rightName = os.path.join(dir_input, 'right_' + str(photo_counter).zfill(2) + '.png')

# 'path/to/rectified_left_image.jpg'
img_left = cv2.imread(leftName, cv2.IMREAD_GRAYSCALE)
img_right = cv2.imread(rightName, cv2.IMREAD_GRAYSCALE)

# Step 3: Create a Stereo Block Matching (SBM) Object
# Now, we will create a Stereo Block Matching (SBM) object, which is a popular method for estimating disparity. OpenCV provides the StereoBM_create() function to create an SBM object:

num_disparities = 16 * 5  # Must be divisible by 16 (default, from source text: 16 * 5)
block_size = 15  # Must be an odd number (default, from source text: 15)

# sbm = cv2.StereoBM_create(numDisparities=num_disparities, blockSize=block_size)
sbm = cv2.StereoSGBM_create(numDisparities=num_disparities, blockSize=block_size)

# The num_disparities parameter defines the number of disparity levels, and the block_size parameter specifies the size of the block window used for matching.

# Step 4: Compute the Disparity Map
# Next, we’ll compute the disparity map using the compute() method of the SBM object:

disparity = sbm.compute(img_left, img_right)

# Step 5: Normalize and Display the Disparity Map
# Finally, we’ll normalize the disparity map to a range of 0 to 255 and display it using OpenCV’s imshow() function:

norm_disparity = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

cv2.imshow('Disparity Map', norm_disparity)
cv2.waitKey(0)
cv2.destroyAllWindows()
