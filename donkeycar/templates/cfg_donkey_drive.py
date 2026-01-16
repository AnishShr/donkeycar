import os
#
# FILE PATHS
#
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')

#
# VEHICLE loop
#
DRIVE_LOOP_HZ = 20      # the vehicle loop will pause if faster than this speed.
MAX_LOOPS = None        # the vehicle loop can abort after this many iterations, when given a positive integer.

DONKEY_GYM = False

# Image Socket Streamer Configuration
STREAM_PORT = 5555
JPEG_QUALITY = 80

# CAMERA configuration
#
CAMERA_TYPE = "PICAM"   # (PICAM|WEBCAM|CVCAM|CSIC|V4L|D435|MOCK|IMAGE_LIST)
IMAGE_W = 160
IMAGE_H = 120
IMAGE_DEPTH = 3         # default RGB=3, make 1 for mono
CAMERA_FRAMERATE = DRIVE_LOOP_HZ
CAMERA_VFLIP = False
CAMERA_HFLIP = False
CAMERA_INDEX = 0  # used for 'WEBCAM' and 'CVCAM' when there is more than one camera connected
# For CSIC camera - If the camera is mounted in a rotated position, changing the below parameter will correct the output frame orientation
CSIC_CAM_GSTREAMER_FLIP_PARM = 0 # (0 => none , 4 => Flip horizontally, 6 => Flip vertically)
BGR2RGB = False  # true to convert from BRG format to RGB format; requires opencv

# LIDAR
USE_LIDAR = True

LIDAR_LOWER_LIMIT = 225 # angles that will be recorded. Use this to block out obstructed areas on your car, or looking backwards.
LIDAR_UPPER_LIMIT = 135

LIDAR_SCAN_TIME = 1.0                   # maximum age of lidar scan values in seconds to be considered valid
LIDAR_MEASUREMENT_SPREAD = 8            # how many degrees to spread the measurements, for error prevention

LIDAR_MIN_LOOKAHEAD = 1.0

LIDAR_VALIDATION_TOLERANCES = {         # validation tolerances for testing
    0: 0.01,
    3000: 0.02,
    5000: 0.025
}

USE_CONSTANT_THROTTLE_STEERING = False
CONSTANT_STEERING = 0.0
CONSTANT_THROTTLE = 0.7

USE_REMOTE_UDP_CONTROLLER = True
REMOTE_CONTROL_PORT = 5001

# DRIVE TRAIN TYPE
DRIVE_TRAIN_TYPE = "PWM_STEERING_THROTTLE"

#
# PWM_STEERING_THROTTLE drivetrain configuration
#
# Drive train for RC car with a steering servo and ESC.
# Uses a PwmPin for steering (servo) and a second PwmPin for throttle (ESC)
# Base PWM Frequence is presumed to be 60hz; use PWM_xxxx_SCALE to adjust pulse with for non-standard PWM frequencies
#
PWM_STEERING_THROTTLE = {
    "PWM_STEERING_PIN": "PIGPIO.BCM.13",   # PWM output pin for steering servo
    "PWM_STEERING_SCALE": 1.0,              # used to compensate for PWM frequency differents from 60hz; NOT for adjusting steering range
    "PWM_STEERING_INVERTED": False,         # True if hardware requires an inverted PWM pulse
    "PWM_THROTTLE_PIN": "PIGPIO.BCM.18",   # PWM output pin for ESC
    "PWM_THROTTLE_SCALE": 1.0,              # used to compensate for PWM frequence differences from 60hz; NOT for increasing/limiting speed
    "PWM_THROTTLE_INVERTED": False,         # True if hardware requires an inverted PWM pulse
    "STEERING_LEFT_PWM": 380,               #pwm value for full left steering
    "STEERING_RIGHT_PWM": 285,              #pwm value for full right steering
    "THROTTLE_FORWARD_PWM": 305,            #pwm value for max forward throttle
    "THROTTLE_STOPPED_PWM": 260,            #pwm value for no movement
    "THROTTLE_REVERSE_PWM": 240,            #pwm value for max reverse throttle
}

# Logging
HAVE_CONSOLE_LOGGING = True
LOGGING_LEVEL = "INFO"
LOGGING_FORMAT = '%(message)s'