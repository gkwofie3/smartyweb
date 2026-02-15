from Zenoph.Notify.Request.NotifyRequest import NotifyRequest
from Zenoph.Notify.Response.MessageResponse import MessageResponse
from Zenoph.Notify.Enums.ContentType import ContentType

class DestinationDeliveryRequest(NotifyRequest):
    #
    #
    def __init__(self, ap):
        super().__init__(ap)

        self.__messageIds = []
        self.__batchId = None

    #
    #
    def setBatchId(self, messageId):
        if messageId is None or not isinstance(messageId, str) or len(messageId) == 0:
            raise Exception("Invalid message reference for destinations delivery request.")

        self.__batchId = messageId

    #
    #
    def addMessageId(self, messageId: str):
        if messageId is None or not isinstance(messageId, str) or len(messageId) == 0:
            raise Exception("Invalid message identifier for destinations delivery request.")

        self.__messageIds.append(messageId)

    #
    #
    def __validate(self):
        # message reference is required
        if self.__batchId is None:
            raise Exception("Message reference has not been set for destinations delivery request.")

        if self.__messageIds is None or len(self.__messageIds) == 0:
            raise Exception("There are no message identifiers for destinations delivery request.")

    #
    #
    def submit(self):
        self.__validate()
        self._setRequestResource("report/message/delivery/destinations/" + self.__batchId)

        if len(self.__messageIds) > 5000:
            self._setResponseContentType(ContentType.GZBIN_XML)

        self._initHttpRequest()
        writer = self._createDataWriter()
        self._requestData = writer.writeDestinationsDeliveryRequest(self.__messageIds)

        # submit for response
        return MessageResponse.create(super().submit())
