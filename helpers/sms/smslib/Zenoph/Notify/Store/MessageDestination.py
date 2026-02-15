from datetime import datetime

from Zenoph.Notify.Utils.RequestUtil import RequestUtil
from Zenoph.Notify.Enums.DestinationStatus import DestinationStatus

class MessageDestination:
    def __init__(self):
        self.__phoneNumber: str = None
        self.__country: str = None
        self.__messageId: str = None
        self.__message: str = None
        self.__status: DestinationStatus = None
        self.__submitDateTime: datetime = None
        self.__reportDateTime: datetime = None
        self.__messageCount: int = 0
        self.__statusId: int = 0
        self.__data: object = None

    @staticmethod
    def create(p: dict):
        if p is None or not isinstance(p, dict):
            raise Exception("Invalid object reference for creating message destination data.")

        destInfo = MessageDestination()

        # check for phone number
        if "phoneNumber" in p:
            destInfo.__phoneNumber = p["phoneNumber"]

        # country
        if "country" in p:
            destInfo.__country = p["country"]

        # destination message Id
        if "messageId" in p:
            destInfo.__messageId = p["messageId"]

        # message 
        if "message" in p:
            destInfo.__message = p["message"]

        # destination status Id (numeric value)
        if "statusId" in p:
            destInfo.__statusId = int(p["statusId"])
            MessageDestination.__setDestinationStatus(destInfo)

        # message count
        if "messageCount" in p:
            destInfo.__messageCount = int(p["messageCount"])

        # personalised values (in the case of personalised SMS)
        if "psndValues" in p:
            destInfo.__data = p["psndValues"]

        # date and time message was submitted
        if "submitDateTime" in p:
            destInfo.__submitDateTime = datetime.strptime(p["submitDateTime"], RequestUtil.DATE_TIME_FORMAT)

        # date and time for delivery report
        if "reportDateTime" in p:
            destInfo.__reportDateTime = datetime.strptime(p["reportDateTime"], RequestUtil.DATE_TIME_FORMAT)

        # return the message destination info
        return destInfo

    #
    # sets destination status
    @staticmethod
    def __setDestinationStatus(destInfo):
        destInfo._status = DestinationStatus(destInfo.__statusId)

    #
    # gets message count
    def getMessageCount(self) ->int:
        return self.__messageCount

    #
    # gets destination phone number
    def getPhoneNumber(self) ->str:
        return self.__phoneNumber

    #
    # gets destination country name
    def getCountry(self) ->str:
        return self.__country

    #
    # gets message Id
    def getMessageId(self) ->str:
        return self.__messageId

    #
    # gets message 
    def getMessage(self) ->str:
        return self.__message

    #
    # gets destination status
    def getStatus(self) ->DestinationStatus:
        return self.__status

    #
    # gets id for the status
    def getStatusId(self) ->int:
        return self.__statusId

    #
    # gets date and time message was submitted
    def getSubmitDateTime(self) ->datetime:
        return self.__submitDateTime

    #
    # gets date and time report was received
    def getReportDateTime(self) ->datetime:
        return self.__reportDateTime

    #
    # gets custom data associated with the destination for the message
    def getData(self) ->object:
        return self.__data