from .EzMLStream import EzMLStream
import cv2
from PIL import Image

class EzMLWebCamStream(EzMLStream):
    """Creates an EzML Stream for web cam using opencv

    """
    def __init__(self, cam_id=0):
        """ 
        :param cam_id: Index of needed camera
        """
        super().__init__()
        self.cap = cv2.VideoCapture(cam_id)
    
    def get_frame(self):
        """Must return pil image 

        """
        r, frame = self.cap.read()

        if r:
            return Image.fromarray(frame)
        else:
            return None

class EzMLLocalVideoStream(EzMLStream):
    """Create a EzML stream for video handling.
    All that is needed to create an EzMLStream child class is too implement the get_frame function that should return the PIL image.
    When None is returned the stream is stopped. Used for infering real time on local video
    """ 
    def __init__(self, url, res=None):
        super().__init__()
        self.cap = cv2.VideoCapture(url)
        self.res = res
        
    def get_frame(self):
        r, frame = self.cap.read()
        
        frame = Image.fromarray(frame)

        if self.res: # TODO check conditions
            frame = frame.resize(self.res)
        
        if r:
            return frame
        else: 
            return None