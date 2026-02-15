from enum import Enum

class HttpStatusCode(Enum):
    OK = 200
    ERROR_BAD_REQUEST = 400
    ERROR_UNAUTHORIZED = 401
    ERROR_FORBIDDEN = 403
    ERROR_METHOD_NOT_ALLOWED = 405
    ERROR_NOT_ACCEPTABLE = 406
    ERROR_UNPROCESSABLE = 422
    ERROR_NOT_FOUND = 404
    ERROR_INTERNAL = 500

    def __int__(self):
        return self.value