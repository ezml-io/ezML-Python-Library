import requests
import os 
from .Errors import FailedAuth, NotAuthed

class EzMLCredentials():
    
    def __init__(self, user: str = None, password: str = None):
        self._url = "https://ezml.io"
        self.token = None

        if user and password:
            self.__login_standard(user, password)
        else:
            self.__load_local()

    def is_authed(self):
        return self.token != None

    def __load_local(self):
        """Loads user/pass from enviroment
            Checks keys:
                - EZML_USER - username or email 
                - EZML_PASS - password 

        """
        user = os.getenv("EZML_USER")
        password = os.getenv("EZML_PASS")

        if user and password:
            self.__login_standard(user, password)
        else:
            raise FailedAuth("Failed loading env variables (EZML_USER & EZML_PASS)")

        
    def __login_standard(self, user: str = None, password: str = None):
        if user and password:
            try:
                r = requests.post(f"{self._url}/api/user/logins", {"user": user, "password": password})
                self.token = r.json()["token"]
            except Exception:
                # wrong credentials
                raise FailedAuth("Incorrect credentials")
        else:
            raise FailedAuth("Invalid values passed")

    def _send_authed_req(self, url: str, method: str, data: dict = {}):
        """
        Sends authed request

        :param url: Appended path to server url
        :param method: GET/POST/UPDATE/DELETE
        :param data: dictionary with data only for supported methods  

        :return: returns result of req
        """
        if self.token:
            if method.lower() == "get":
                return requests.get(self._url + url, headers={'Authorization': f'Bearer {self.token}'})
            elif method.lower() == "post":
                return requests.post(self._url + url,data, headers={'Authorization': f'Bearer {self.token}'})
            else:
                raise NotImplementedError() # unsupported type 
                # TODO Implement other types
        else:
            raise NotAuthed("Token isn't loaded")

        
