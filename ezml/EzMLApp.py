from .EzMLCredentials import EzMLCredentials
from .EzMLStream import EzMLStream
import cv2 
from PIL import Image
import numpy as np
import os 
import filetype
import io
import requests 

from .Errors import FailedDeployment, NotDeployed, InvalidImage, InvalidVideo

class EzMLApp:

    def __init__(self, app_id, user: str = None, password: str = None, credentials = None):
        ''' 
        if isinstance(credentials, EzMLCredentials) and credentials.is_authed():
            self.credentials = credentials
        else:
            self.credentials = EzMLCredentials(user, password)
        '''
        self.app_id = app_id
        self.deployment_id = None
        self.deployed = False 
        # self.server_url = None
        self.server_url = "localhost"
        self.FLASK_PORT = 8001
        self.UDP_PORT = 5000

    def deploy(self):
        """Deploy application, this should always be called before infering
        """
        try:
            self.credentials._send_authed_req(f"/api/application/{self.app_id}/deployments", "post")

            deployment = self.credentials._send_authed_req(f"/api/application/{self.app_id}/active-deployment", "get")
            
            deployment = deployment.json()["deployment"]
            
            self.deployment_id = deployment["id"]
            self.server_url = deployment["host"]
            
            self.deployed = True
        except Exception: # TODO less braod exceptions
            raise FailedDeployment("Failed starting deployment")
    
    def __check_deployment(self):
        if not self.deployed:
            raise NotDeployed("Not deployed")

    def __valid_result(self, res):
        return "error" not in res # keep simple

    def stream_to_server(self, StreamClass, verbose = 2, res = (300, 300), timeout=1):
        """Streams to server using custom class
            Returns a generator that you can iterator over

            :param StreamClass: Class that inherits the abstract class EzMLStream
            :param res: Resolution images should be sent as eg. (300, 300)
            :param verbose: Sets verbose level (breakdown belkow)
            :param timeout: Sets max timeout for frame retrieval

            verbose = 2, everything
            verbose = 1, only fps
            verbose = 0, none
        """
        self.__check_deployment()

        if isinstance(StreamClass, EzMLStream):
            for result, frame in StreamClass._stream_to_server((self.server_url, self.UDP_PORT), verbose, res = res, timeout=timeout):
                if self.__valid_result(result):
                    yield result, frame
        else:
            raise TypeError()

    def __build_http_url(self, *args):
        return "http://" + self.server_url + f":{self.FLASK_PORT}" + '/'.join(['',*args])

    

    def _infer_on_binary(self, b, url="infer"):
        r = requests.post(self.__build_http_url(url), files={'file': b})
        return r.json()
    
    @staticmethod
    def _draw_rectangle_with_text(frame, text, top_coord, bot_coord):
        (text_width, text_height), _ = cv2.getTextSize(text ,cv2.FONT_HERSHEY_COMPLEX,0.5,2)
        cv2.rectangle(frame, top_coord, bot_coord, (255,0,0), 2)
        x,y = top_coord
        cv2.putText(frame, text, (x, y - text_height), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    @staticmethod
    def _layer_results(frame, results):
        """Layers results onto frame, returns np/cv2 frame with detections drawn
        """
        frame = np.asarray(frame)
        h, w, _ = frame.shape

        for k, v in results.items():
            # k is pipe name v is actual results
            for detection in v: # TODO add nesting support
                detection = detection['detection']
                EzMLApp._draw_rectangle_with_text(frame, f"{k}:{detection['class_name'] if 'class_name' in detection else detection['word']} {(float(detection['class_confidence']) * 100):.2f}%", (int(detection["left_x"] * w), int(detection["top_y"] * h)), (int((detection["left_x"] + detection["width"]) * w),int((detection["top_y"] + detection["height"]) * h)))            
        return frame

    @staticmethod
    def display_results(results, frame = np.array([]), img_src = "", save = None, show = False, waitkey=True, conf_threshold = 0.5):
        """Displays results on image

            :param frame: cv2 valid frame (np array)
            :param img_src: Valid image path
            :param save: Location to save image
            :param show: Show in window
            :param waitkey: true/false Should block after image
            :param conf_threshold: Ignore detections with confidence < conf_theshold

            :return: Returns True/False depending on success of save, if not save then nothing is returned
        """
        if not frame.any() and filetype.is_image(img_src):
            frame = cv2.imread(img_src)
        elif not frame.any():
            raise TypeError()

        results = EzMLApp._filter_results(results, conf_threshold)

        frame = EzMLApp._layer_results(frame, results)

        if show:
            cv2.imshow('image', frame)
            if waitkey:
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        if save:
            try:
                cv2.imwrite(save, frame)
                return True
            except Exception:
                print("Error happened while saving image")
                return False 

    @staticmethod
    def _filter_results(results, conf_threshold):
        """ Filters results with confidence < conf_threshold
        """
        for pipe in results:
            results[pipe] = [d for d in results[pipe] if d['detection']['class_confidence'] >= conf_threshold]
        return results

    def __get_buffer(self, image):
        """Returns buffer of given PIL Image

        """ 
        buff = io.BytesIO()
        image.save(buff, format='JPEG')
        buff.seek(0)

        return buff

    def infer_image(self, img_src = None, image = None, save = False, display = False, conf_threshold = 0.5, res = (600, 600)): 
        """Infers on an image

        :param img_src: Path to image
        :param image: Pillow image
        :param save: Path to save file, eg. /path/to/file.png
        :param display: Display image after inference
        :param conf_threshold: Ignore detections with confidence < conf_theshold
        :param res: Resolution as tuple of image to be sent as (only for when img_src is valid)

        :return: Returns results
        """

        # TODO have image not have inverted colors
        


        # self.__check_deployment()

        result = None

        if img_src and os.path.exists(img_src) and filetype.is_image(img_src):
            image = Image.open(img_src)
            result = self._infer_on_binary(self.__get_buffer(image.resize(res)))
        elif image:
            result = self._infer_on_binary(self.__get_buffer(image)) 
        else:
            raise InvalidImage("Invalid image passed to infer_image")
        
        if result: result = EzMLApp._filter_results(result, conf_threshold)

        if display and result:
            if img_src: EzMLApp.display_results(result, img_src=img_src, show=True, save = save)
            elif image: EzMLApp.display_results(result, np.array(image), show=True, save = save)
        elif result and save:
            if img_src: EzMLApp.display_results(result, img_src=img_src, show=False, save = save)
            elif image: EzMLApp.display_results(result, np.array(image), show=False, save = save)

        return result 
    
    def infer_video(self, vid_src, save = None, show = False, conf_threshold=0.5):
        """Infers on video
        
        :param vid_src: path to video
        :param save: Location to save video
        :param show: Display window with results

        :return: Returns the results per frame
        """ 

        if filetype.is_video(vid_src):
            result = self._infer_on_binary(open(vid_src, 'rb'), "infer-video")
            

            fr = 0
            
            cap = cv2.VideoCapture(vid_src)

            size = (int(cap.get(3)), int(cap.get(4)))
            upload_writer = None

            if save:
                fourcc = cv2.VideoWriter_fourcc(*'FMP4')
                upload_writer = cv2.VideoWriter(save, 
                            fourcc,
                            20, size)

            if not save and not show:
                return result

            while cap.isOpened():
                r, frame = cap.read()
                if not r:
                    break

                detections = result[fr]
                detections = EzMLApp._filter_results(detections, conf_threshold)
                frame = EzMLApp._layer_results(frame, detections)

                if save:
                    upload_writer.write(frame)

                if show:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) == ord('q'):
                        show = False
                        cv2.destroyAllWindows()
                fr += 1
            if save:
                upload_writer.release()
            cap.release()
            cv2.destroyAllWindows()

            return result
        else:
            raise InvalidVideo("Invalid video passed to infer_video")


    

