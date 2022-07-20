from PIL import Image
import base64
from io import BytesIO
import random 
import string
import socket
import time
import json
import cv2
import math

def random_string_generator(str_size, allowed_chars=string.ascii_letters):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

class EzMLStream():
    """
    Implements the EzMLStream. This is an abstract class, the implementation of get_frame() is needed for it to work.
    get_frame() must return a PIL image 

    """
    def __init__(self):
        self.MAX_BUFF = 65000
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _convert_image(self, image, res):
        if image == None: return None
        try:
            image = image.resize(res)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception:
            raise TypeError("Output must be a pil image object")


    def _stream_to_server(self, server, verbose=2, res=(300, 300), timeout = 1): # KEEPING IT SIMPLE FOR NOW, BLOCKS UNTIL RESULT
        self.sock.settimeout(timeout)
        # verbose = 1, only fps
        # verbose = 0, none
        start = time.time()
        fps = 0
        while True:
            frame = self.get_frame()
            buffer = self._convert_image(frame, res)
            if buffer == None:
                print("Failed fetching frame")
                break
            buffer_size = len(buffer)
            num_of_packs = 1

            if buffer_size > self.MAX_BUFF:
                num_of_packs = math.ceil(buffer_size / self.MAX_BUFF)

            id = random_string_generator(10)
            frame_info = {
                "id": id,
                "packets": num_of_packs,
                "type": "info"
            }

            self.sock.sendto(json.dumps(frame_info).encode("utf-8"), server)

            left = 0
            right = self.MAX_BUFF

            for i in range(num_of_packs):
                # truncate data to send
                data = buffer[left:right]
                left = right
                right += self.MAX_BUFF

                packet_info = {
                    "id": id,
                    "idx": i, 
                    "type": "frame",
                    "packet": data
                }

                # send the frames accordingly
                self.sock.sendto(json.dumps(packet_info).encode("utf-8"), server)
                if verbose == 2:
                    print(f"Sent packet {i+1}/{num_of_packs}")
            try:
                result, _ = self.sock.recvfrom(self.MAX_BUFF)
            except socket.timeout as e:
                continue
            result = json.loads(result.decode("utf-8"))
            
            
            if verbose > 0:
                fps += 1
                if time.time() - start > 1:
                    print(f"Streaming with {fps} fps")
                    fps = 0
                    start = time.time()
            yield result, frame
        
                

    def get_frame(self):
        '''Should return a PIL image object
        '''
        pass

