import cv2
import logging
import numpy as np
import time
from typing import Callable

def map_frames(video_name: str, callback: Callable[[np.ndarray, int], None]):
    start = time.time()
    vcap = cv2.VideoCapture(video_name)
    success, image = vcap.read()
    count = 0
    while success:
        callback(image, count)
        success, image = vcap.read()
        count += 1
    end = time.time()
    logging.debug("Extracted %s frames in %f seconds", count, end - start)