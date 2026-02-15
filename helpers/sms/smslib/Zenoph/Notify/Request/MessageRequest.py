from abc import ABC

from Zenoph.Notify.Request.ComposeRequest import ComposeRequest
from Zenoph.Notify.Compose.IMessageComposer import IMessageComposer
from Zenoph.Notify.Compose.ISchedule import ISchedule
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Enums.ContentType import ContentType

class MessageRequest(ComposeRequest, IMessageComposer, ISchedule):
    def __init__(self, ap: AuthProfile = None):  
     super().__init__(ap)

    def getBatchId(self) ->str:
        self._assertComposer()
        return self._composer.getBatchId()

    #
    # sets message sender Id
    def setSender(self, sender: str):
        self._assertComposer()
        self._composer.setSender(sender)

    #
    # gets message sender Id
    def getSender(self):
        self._assertComposer()
        return self._composer.getSender()

    #
    # sets message
    def setMessage(self, message: str, extData = None):
        self._assertComposer()
        self._composer.setMessage(message, extData)

    #
    # gets the message
    def getMessage(self):
        self._assertComposer()
        return self._composer.getMessage()

    # gets assigned messageId for destination phone number
    def getMessageId(self, phoneNumber: str) ->str:
        self._assertComposer()
        return self._composer.getMessageId(phoneNumber)

    # checks whether messageId exists or not
    def messageIdExists(self, messageId: str) ->bool:
        self._assertComposer()
        return self._composer.messageIdExists(messageId)


    # whether message will be scheduled or not
    def schedule(self) ->bool:
        self._assertComposer()
        return self._composer.schedule()

    # whether message was scheduled or not
    def isScheduled(self):
        self._assertComposer()
        return self._composer.isScheduled()

    # schedule info
    def getScheduleInfo(self):
        self._assertComposer()
        return self._composer.getScheduleInfo()


    # sets URL for delivery notification
    def setDeliveryCallback(self, url: str, contentType: ContentType):
        self._assertComposer()
        self._composer.setDeliveryCallback(url, contentType)

    # gets notify URL info
    def getDeliveryCallback(self):
        self._assertComposer()
        return self._composer.getDeliveryCallback()


    # set schedule date and time info
    def setScheduleDateTime(self, dateTime, val1 = None, val2 = None):
        self._assertComposer()
        self._composer.setScheduleDateTime(dateTime, val1, val2)

    # validates destination sender Id
    def validateDestinationSenderName(self, phoneNumber):
        self._assertComposer()
        self._composer.validateDestinationSenderName(phoneNumber)

    # refresh scheduled destinations
    def refreshScheduledDestinationsUpdate(self, dests):
        self._assertComposer()
        self._composer.refreshScheduledDestinationsUpdate(dests)

    # removes destination by messageId
    def removeDestinationById(self, messageId: str) ->bool:
        self._assertComposer()
        return self._composer.removeDestinationById(messageId)

    # updates destination by messageId
    def updateDestinationById(self, messageId: str, phoneNumber: str) ->bool:
        self._assertComposer()
        return self._composer.updateDestinationById(messageId, phoneNumber)
