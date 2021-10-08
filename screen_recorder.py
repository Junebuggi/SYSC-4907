import pygetwindow as gw
import numpy as np
import cv2
import time
from mss import mss
from PIL import Image

# Maximize and bring SeekOFix window to the foreground
seekOFixWindow = gw.getWindowsWithTitle('SeekOFix')[0]
seekOFixWindow.maximize()
seekOFixWindow.activate()

# These depend on host resolution
X_OFFSET = 17
Y_OFFSET = 64
VIDEO_WIDTH = 620
VIDEO_HEIGHT = 470

# Monitor for mss (screenshots)
monitor = {'left': X_OFFSET, 'top': Y_OFFSET, 'width': VIDEO_WIDTH, 'height': VIDEO_HEIGHT}

# Resolution for VideoWriter object (video export)
resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)

# MP4 codec
codec = cv2.VideoWriter_fourcc(*'MP4V')

# Timestamped filename
timestamp = time.strftime('%Y.%m.%d-%H.%M.%S')
filename = '{}.mp4'.format(timestamp)
testDataFolder = './Test Data'
videoPath = '{}/{}'.format(testDataFolder, filename)

# Limit image grab rate based on VideoWriter fps
fps = 10.0
counterLimit = (30 / fps)

# Create VideoWriter object
out = cv2.VideoWriter(videoPath, codec, fps, resolution)

# Create empty window
cv2.namedWindow('Live', cv2.WINDOW_NORMAL)

# Resize this window
cv2.resizeWindow('Live', 480, 270)

# Record number of frames and duration to calculate true FPS
numFrames = 0
startTime = time.time()
counter = 0

with mss() as sct:
    while True:
        screenShot = sct.grab(monitor)
        img = Image.frombytes(
            'RGB',
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )

        frame = np.array(img)

        # Convert from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        counter += 1

        # Write an image to the video every X captures
        if counter >= counterLimit:
            counter = 0
            out.write(frame)
            numFrames += 1

            # Display the recording screen
            cv2.imshow('Live', frame)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):

            # Print capture duration and true FPS
            endTime = time.time()
            duration = endTime - startTime
            trueFps = np.ceil(numFrames / duration)
            print('Duration: {}'.format(duration))
            print('True FPS: {}'.format(trueFps))

            # Release the Video writer
            out.release()

            # Destroy all windows
            cv2.destroyAllWindows()
            break
