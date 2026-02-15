from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Response.MessageResponse import MessageResponse
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Request.NotifyRequest import NotifyRequest

class MessageDeliveryRequest(NotifyRequest):
    def __init__(self, ap: AuthProfile = None):
        super().__init__(ap)

        self.__batchId: str = None

    def setBatchId(self, batchId: str):
        if batchId is None or not isinstance(batchId, str) or len(batchId) == 0:
            raise Exception("Invalid message reference for sending delivery status request.")

        # set the reference
        self.__batchId = batchId

    def submit(self):
        # ensure message reference has been set
        if self.__batchId is None:
            raise Exception("Message reference has not been set for sending delivery status request.")

        self._setRequestResource(f"report/message/delivery/{self.__batchId}")
        self._setResponseContentType(ContentType.GZBIN_XML)

        self._initHttpRequest()

        # submit and create response object
        return MessageResponse.create(super().submit())
