import numpy as np
import cv2
from mss import mss
from PIL import Image

# Tweak these for your environment
X_OFFSET = 17
Y_OFFSET = 66
VIDEO_WIDTH = 620
VIDEO_HEIGHT = 470

# Monitor for mss (screenshots)
monitor = {'left': X_OFFSET, 'top': Y_OFFSET, 'width': VIDEO_WIDTH, 'height': VIDEO_HEIGHT}

# Resolution for VideoWriter object (video export)
resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)

# MP4 codec
codec = cv2.VideoWriter_fourcc(*'MP4V')

# Filename
filename = './Test Data/recording.mp4'

# TODO: Figure out how to output a video that is accurate wrt time
# FPS
fps = 30.0

# Create VideoWriter object
out = cv2.VideoWriter(filename, codec, fps, resolution)

# Create empty window
cv2.namedWindow('Live', cv2.WINDOW_NORMAL)

# Resize this window
cv2.resizeWindow('Live', 480, 270)

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

        # TODO: Consider writing to output after X amount of frames to
        # reduce file size and then lower FPS
        out.write(frame)

        # Display the recording screen
        cv2.imshow('Live', frame)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            # Release the Video writer
            out.release()

            # Destroy all windows
            cv2.destroyAllWindows()
            break
