from Zenoph.Notify.Enums.RequestHandshake import RequestHandshake

class RequestException(Exception):
    def __init__(self, message: str, hshk: RequestHandshake):
        self.message = message
        self.__handshake = hshk

        super().__init__(message)

    def __str__(self):
        return self.message

    def getRequestHandshake(self) ->RequestHandshake:
        return self.__handshake
