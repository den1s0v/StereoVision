import cv2
import numpy as np
import threading
# from time import sleep

from user_settings import CAMERA_SENSOR_ID_LEFT, CAMERA_SENSOR_ID_RIGHT

"""
Run this script to verify your cameras configuration. Hit 'Q' key to exit.
"""


class Start_Cameras:

    def __init__(self, sensor_id):
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

        self.sensor_id = sensor_id

        # gstreamer_pipeline_string = self.gstreamer_pipeline()
        # self.open(gstreamer_pipeline_string)
        self.open(sensor_id)

    # Opening the cameras
    def open(self,
             # gstreamer_pipeline_string
             sensor_id
             ):
        # gstreamer_pipeline_string = self.gstreamer_pipeline()
        try:
            self.video_capture = cv2.VideoCapture(
                # gstreamer_pipeline_string, cv2.CAP_GSTREAMER
                sensor_id
            )
            grabbed, frame = self.video_capture.read()
            print(f"Camera {sensor_id} is opened")

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("sensor_id: " + sensor_id)
            # print("Pipeline: " + gstreamer_pipeline_string)
            return
        # Grab the first frame to start the video capturing
        self.grabbed, self.frame = self.video_capture.read()

    # Starting the cameras
    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture != None:
            self.running = True
            self.read_thread = threading.Thread(target=self.updateCamera, daemon=True)
            self.read_thread.start()
        return self

    def stop(self):
        self.running = False
        self.read_thread.join()

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            except RuntimeError:
                print("Could not read image from camera")
            # sleep(0.3)

    def read(self) -> 'grabbed, frame':
        try:
            with self.read_lock:
                frame = self.frame.copy()
                grabbed = self.grabbed
            return grabbed, frame
        except:
            print("Error while read()`ing image from camera")
            return False, None

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()

    # Currently there are setting frame rate on CSI Camera on Nano through gstreamer
    # Here we directly select sensor_mode 3 (1280x720, 59.9999 fps)
    def gstreamer_pipeline(self,
                           sensor_mode=3,
                           capture_width=1280,
                           capture_height=720,
                           display_width=640,
                           display_height=360,
                           framerate=30,
                           flip_method=0,
                           ):
        return (
                "nvarguscamerasrc sensor-id={self.sensor_id} sensor-mode=%d ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                % (
                    # self.sensor_id,
                    sensor_mode,
                    capture_width,
                    capture_height,
                    framerate,
                    flip_method,
                    display_width,
                    display_height,
                )
        )


def get_cameras() -> 'left, right':
    """
        HP Pav15 config:
        0: notebook camera
        3: cyberlink virtual camera

        1, 2: usb camera

        (Помогает, если одну из камер подключить к порту USB 2.0, а вторую - к порту USB 3)
    """

    left_camera = Start_Cameras(CAMERA_SENSOR_ID_LEFT).start()
    ###
    # right_camera = left_camera
    ###
    right_camera = Start_Cameras(CAMERA_SENSOR_ID_RIGHT).start()

    # right_camera = Start_Cameras('http://192.168.43.24:8383/cam_1.cgi').start()

    return left_camera, right_camera


# This is the main. Read this first.
if __name__ == "__main__":
    left_camera, right_camera = get_cameras()

    while True:
        right_grabbed, right_frame = right_camera.read()
        left_grabbed, left_frame = left_camera.read()

        if left_grabbed and right_grabbed:
            images = np.hstack((left_frame, right_frame))
            cv2.imshow("Camera Images", images)
            k = cv2.waitKey(1) & 0xFF

            if k == ord('q'):
                break
        else:
            break

    left_camera.stop()
    left_camera.release()
    right_camera.stop()
    right_camera.release()
    cv2.destroyAllWindows()
