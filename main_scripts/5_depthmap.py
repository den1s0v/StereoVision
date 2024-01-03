import collections
import json

import cv2
import numpy as np
from stereovision.calibration import StereoCalibration

from start_cameras import get_cameras


# Depth map default preset
SWS = 5
PFS = 5
PFC = 29
MDS = -30
NOD = 160
TTH = 100
UR = 10
SR = 14
SPWS = 100


MEAN_QUEUE_MAX_SIZE = 3
MEAN_QUEUE = collections.deque(maxlen=MEAN_QUEUE_MAX_SIZE)

def filter_consequent_frames(disparity_normalized):
    ###
    # take mean of several latest pictures
    if MEAN_QUEUE_MAX_SIZE:
        # replace zeros with nan to mark unknown area
        frame = np.where(disparity_normalized > 0, disparity_normalized, np.nan)
        # push to queue
        if len(MEAN_QUEUE) >= MEAN_QUEUE_MAX_SIZE:
            MEAN_QUEUE.popleft()
        MEAN_QUEUE.append(frame)

        # calc mean over queued frames
        mean_frame = sum(MEAN_QUEUE) / MEAN_QUEUE_MAX_SIZE

        np.nan_to_num(mean_frame, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        return mean_frame
    else:
        return disparity_normalized



def load_map_settings(file):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings, sbm
    print('Loading parameters from file...')
    f = open(file, 'r')
    data = json.load(f)
    f.close()

    # loading data from the json file and assigning it to the Variables
    SWS = data['SADWindowSize']
    PFS = data['preFilterSize']
    PFC = data['preFilterCap']
    MDS = data['minDisparity']
    NOD = data['numberOfDisparities']
    TTH = data['textureThreshold']
    UR = data['uniquenessRatio']
    SR = data['speckleRange']
    SPWS = data['speckleWindowSize']

    # changing the actual values of the variables
    if False:
        sbm = cv2.StereoBM_create(numDisparities=16, blockSize=SWS)
        sbm.setPreFilterType(1)
        sbm.setPreFilterSize(PFS)
        sbm.setPreFilterCap(PFC)
        sbm.setMinDisparity(MDS)
        sbm.setNumDisparities(NOD)
        sbm.setTextureThreshold(TTH)
        sbm.setUniquenessRatio(UR)
        sbm.setSpeckleRange(SR)
        sbm.setSpeckleWindowSize(SPWS)
    else:
        sbm = cv2.StereoSGBM_create(numDisparities=16, blockSize=SWS)
        # sbm.setPreFilterType(1)
        # sbm.setPreFilterSize(PFS)
        sbm.setPreFilterCap(PFC)
        sbm.setMinDisparity(MDS)
        sbm.setNumDisparities(NOD)
        # sbm.setTextureThreshold(TTH)
        sbm.setUniquenessRatio(UR)
        sbm.setSpeckleRange(SR)
        sbm.setSpeckleWindowSize(SPWS)

    print('Parameters loaded from file ' + file)


def stereo_depth_map(rectified_pair):
    # blockSize is the SAD Window Size

    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    disparity_normalized = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)

    ###
    # take mean of several latest pictures
    # replace variable
    disparity_normalized = filter_consequent_frames(disparity_normalized)
    ###

    image = np.array(disparity_normalized, dtype=np.uint8)
    disparity_color = cv2.applyColorMap(image, cv2.COLORMAP_JET)
    return disparity_color, disparity_normalized


def onMouse(event, x, y, flag, disparity_normalized):
    if event == cv2.EVENT_LBUTTONDOWN:
        distance = disparity_normalized[y][x]
        print("Distance in centimeters {}".format(distance))
        return distance


if __name__ == "__main__":
    # left_camera = Start_Cameras(0).start()
    # right_camera = Start_Cameras(1).start()
    left_camera, right_camera = get_cameras()
    load_map_settings("../3dmap_set.txt")

    cv2.namedWindow("DepthMap")
    calibration = StereoCalibration(input_folder='../calib_result')

    while True:
        left_grabbed, left_frame = left_camera.read()
        right_grabbed, right_frame = right_camera.read()

        if left_grabbed and right_grabbed:
            # Convert BGR to Grayscale
            left_gray_frame = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
            right_gray_frame = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)

            # calling all calibration results
            rectified_pair = calibration.rectify((left_gray_frame, right_gray_frame))
            disparity_color, disparity_normalized = stereo_depth_map(rectified_pair)

            # Mouse clicked function
            cv2.setMouseCallback("DepthMap", onMouse, disparity_normalized)

            # Show depth map and image frames
            output = cv2.addWeighted(left_frame, 0.5, disparity_color, 0.5, 0.0)
            cv2.imshow("DepthMap", np.hstack((disparity_color, output)))

            cv2.imshow("Frames", np.hstack((left_frame, right_frame)))

            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break

            else:
                continue

    left_camera.stop()
    left_camera.release()
    right_camera.stop()
    right_camera.release()
    cv2.destroyAllWindows()
