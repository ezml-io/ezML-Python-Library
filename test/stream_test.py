from ezml import EzMLApp, EzMLCredentials, EzMLLocalVideoStream
import cv2
from PIL import Image
import numpy as np


app = EzMLApp("app_id", credentials=EzMLCredentials("username", "password"))  # Creates EzMLApp instance, with credentials
app.deploy() # deploy app


vid_src = "vid_src"

stream = EzMLLocalVideoStream(vid_src)

for result, frame in app.stream_to_server(stream, 1): # stream_to_server is a generator that yields the result and frame.
    frame = np.asarray(frame)
    EzMLApp.display_results(result, frame, show=True, waitkey=False) # displays result in window
    
    if cv2.waitKey(1) == ord('q'):
        break        