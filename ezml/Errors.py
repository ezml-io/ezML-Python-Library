# CREDENTIALS ERRORS

class FailedAuth(Exception):
    """Exceptions raised when auth is failed

    """
    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message 

class NotAuthed(Exception):
    """Exceptions raised when operation is attempted while not authed

    """
    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message 


# App errors

class FailedDeployment(Exception):
    """Exceptions raised when deployment fails

    """
    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message 


class NotDeployed(Exception):
    """Exceptions raised when operation is attempted while App isn't deployed

    """
    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message


class InvalidImage(Exception):
    """ Exception raised when invalid image is passed into functions

    """ 

    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message

class InvalidVideo(Exception):
    """ Exception raised when invalid video is passed into functions

    """ 

    def __init__(self, message):
        self.message = message 
        super().__init__(message)

    def __str__(self):
        return self.message