# user_settings.py

""" Constants used in other scripts are defined here. Modify them as you need before running the scripts. """


# SETTINGS FOR: 'start_cameras.py'

"""
    Example laptop config:
    0: notebook camera
    3: cyberlink virtual camera (software device)

    1, 2: usb camera

    (Помогает, если одну из камер подключить к порту USB 2.0 через USB-hub, а вторую - к порту USB 3)
"""
CAMERA_SENSOR_ID_LEFT  = 0
CAMERA_SENSOR_ID_RIGHT = 2


# SETTINGS FOR:
# 1_taking_pictures.py

total_photos = 60  # Number of images to take and process thereafter



# SETTINGS FOR:
# 2_image_selection.py
# 3_calibration.py

# img_height = 360
img_height = 480
img_width = 640



# SETTINGS FOR:
# 3_calibration.py

# Chessboard parameters
# (Must use 6 Rows and 9 Column chessboard)
rows = 6
columns = 9
square_size = 2.5


