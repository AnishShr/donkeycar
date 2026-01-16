#!/usr/bin/env python3
"""
Script to stream camera images over web interface.

Usage:
    img_socket_streamer.py (drive) [--log=INFO]

Options:
    -h --help          Show this screen.
    --log=<level>      Log level [default: INFO].
"""

import os
import logging
import threading
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    import cv2
    import numpy as np
except:
    pass

from flask import Flask, Response, render_template_string
from docopt import docopt

import donkeycar as dk
from donkeycar.templates.complete import add_camera
from donkeycar.parts.lidar import RPLidar2, ScanFilter
from donkeycar.parts.remote_controller import RemoteControllerUDP
from donkeycar.templates.complete import add_drivetrain

HOST_PC_IP = "10.232.53.79"
UDP_PORT = 7000

app = Flask(__name__)

class ImageWebStreamer:
    def __init__(self, cfg):
        self.port = cfg.STREAM_PORT
        self.jpeg_quality = cfg.JPEG_QUALITY
        self.image = None
        self.running = True
        self.lock = threading.Lock()

    def get_frame(self):
        with self.lock:
            if self.image is not None:
                # Convert RGB to BGR for cv2
                img_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
                _, encoded = cv2.imencode(
                    '.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
                )
                return encoded.tobytes()
        return None

    def update(self):
        """Background thread - runs Flask server"""
        logger.info(f"Web stream available at http://0.0.0.0:{self.port}")
        app.run(host='0.0.0.0', port=self.port, threaded=True, use_reloader=False)

    def run_threaded(self, image):
        """Called by vehicle loop - updates the image"""
        with self.lock:
            self.image = image

    def shutdown(self):
        self.running = False
        logger.info("ImageWebStreamer shutdown")


# Global streamer reference for Flask routes
streamer = None


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>DonkeyCar Stream</title>
    <style>
        body { 
            background: #1a1a1a; 
            display: flex; 
            flex-direction: column;
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            margin: 0;
            font-family: Arial, sans-serif;
        }
        h1 { color: #fff; }
        img { 
            border: 2px solid #444; 
            border-radius: 8px;
            max-width: 90vw;
        }
    </style>
</head>
<body>
    <h1>DonkeyCar Camera Stream</h1>
    <img src="/video_feed" alt="Camera Stream">
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame = streamer.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


def drive(cfg):
    """
    Construct a vehicle to stream camera images over web.
    """
    global streamer

    V = dk.vehicle.Vehicle()

    # Initialize logging
    if cfg.HAVE_CONSOLE_LOGGING:
        logger.setLevel(logging.getLevelName(cfg.LOGGING_LEVEL))
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(cfg.LOGGING_FORMAT))
        logger.addHandler(ch)

    if cfg.USE_REMOTE_UDP_CONTROLLER:

        # steering = getattr(cfg, 'CONSTANT_STEERING', 0.0)
        # throttle = getattr(cfg, 'CONSTANT_THROTTLE', 0.3)

        controller = RemoteControllerUDP(host='0.0.0.0', port=cfg.REMOTE_CONTROL_PORT)    
        V.add(controller, outputs=['steering', 'throttle'], threaded=True)
        add_drivetrain(V, cfg)  

        # Add camera
        add_camera(V, cfg, camera_type='single')

        # Add web streamer
        streamer = ImageWebStreamer(cfg)
        V.add(streamer, inputs=['cam/image_array'], threaded=True)

        logger.info("=" * 50)
        logger.info(f"Web stream at http://<PI_IP>:{cfg.STREAM_PORT}")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 50)

        if cfg.USE_LIDAR:
            lidar = RPLidar2(min_angle=cfg.LIDAR_LOWER_LIMIT, max_angle=cfg.LIDAR_UPPER_LIMIT, udp_host=HOST_PC_IP, udp_port=UDP_PORT)
            V.add(lidar, outputs=['lidar/measurements'], threaded=True)

            filt = ScanFilter(min_angle=cfg.LIDAR_LOWER_LIMIT, max_angle=cfg.LIDAR_UPPER_LIMIT, measurement_spread = cfg.LIDAR_MEASUREMENT_SPREAD, time_window=cfg.LIDAR_SCAN_TIME, udp_host=HOST_PC_IP, udp_port=UDP_PORT)
            V.add(filt, inputs=['lidar/measurements'], outputs=['lidar/filtered_measurements'])

        logger.info("Press Ctrl+C to stop")
        V.start(rate_hz=cfg.DRIVE_LOOP_HZ, max_loop_count=cfg.MAX_LOOPS)
        return


if __name__ == '__main__':
    args = docopt(__doc__)
    cfg = dk.load_config()

    log_level = args['--log'] or "INFO"
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logging.basicConfig(level=numeric_level)

    if args['drive']:
        drive(cfg)