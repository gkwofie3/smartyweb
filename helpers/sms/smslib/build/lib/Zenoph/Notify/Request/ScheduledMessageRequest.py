from datetime import datetime

from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Response.MessageResponse import MessageResponse
from Zenoph.Notify.Build.Reader.MessagePropertiesReader import MessagePropertiesReader
from Zenoph.Notify.Request.NotifyRequest import NotifyRequest

class ScheduledMessageRequest(NotifyRequest):
    __BASE_RESOURCE__ = "message/scheduled"

    def __init__(self, ap: AuthProfile = None):
        # base constructor call
        super().__init__(ap)

        self.__category: MessageCategory = MessageCategory.SMS
        self.__fromDateTime: datetime = None
        self.__toDateTime: datetime = None
        self.__utcOffset: str = None
        self.__batchId: str = None

    def __validateDates(self):
        if self.__fromDateTime is not None and self.__toDateTime is None:
            raise Exception("'Date From' has not been set for scheduled message request.")

        if self.__fromDateTime is None and self.__toDateTime is not None:
            raise Exception("'Date To' has not been set for scheduled message request.")

    def __prepareScheduledLoadParams(self):
        return {
                "category": self.__category,
                'dateFrom': self.__fromDateTime,
                'dateTo': self.__toDateTime,
                'offset': self.__utcOffset,
                'batch': self.__batchId
            }

    def __loadScheduled(self):
        # at least message category should be set
        if self.__category is None:
            raise Exception("Message category has not been set for loading scheduled messages.")

        self._setRequestResource("%s/%s%s" % (ScheduledMessageRequest.__BASE_RESOURCE__, "load", "" if self.__batchId is None else "/" + self.__batchId))
        self._setResponseContentType(ContentType.GZBIN_XML)

        # initialise request writing
        self._initHttpRequest()

        # If message batch identifier is specified, then it means we are to
        # load a specific message. In this case, the batch Id will be inserted
        # as part of the URL so there won't be any need to write additional 
        # information about messages to be loaded
        if self.__batchId is None:
            writer = self._createDataWriter()
            self._requestData = writer.getScheduledMessagesLoadRequestData(self.__prepareScheduledLoadParams())

        # submit for response
        return self.__createMessges(super().submit().getDataFragment())

    def loadMessages(self, category: MessageCategory, dateFrom: datetime = None, dateTo: datetime = None, offset: str = None):
        if not isinstance(category, MessageCategory):
            raise Exception("Invalid message category for loading scheduled messages.")

        self.__category = category

        # this is not for a single message so set reference and utc offset are not needed
        self.__batchId = None
        self.__utcOffset = None

        # we don't expect one date and time to be set whiles the other is not set
        if (dateFrom is None and dateTo is not None) or (dateFrom is not None and dateTo is None):
            raise Exception("Invalid date and time specifiers for loading scheduled messages.")

        if dateFrom is not None and dateTo is not None:
            if not isinstance(dateFrom, datetime) or not isinstance(dateTo, datetime):
                raise Exception("Invalid date and time specifiers or loading scheduled messages.")

        # if UTC offset is provided, validate and set
        if isinstance(offset, str) and len(offset) > 0:
            if not MessageUtil.isValidTimeZoneOffset(offset):
                raise Exception("Invalid UTC offset for loading scheduled messages.")
            else:
                self.__utcOffset = offset

        self.__fromDateTime = dateFrom
        self.__toDateTime = dateTo

        # validate the dates
        self.__validateDates()

        # load and return messages
        return self.__loadScheduled()

    def loadMessage(self, batchId: str):
        if not isinstance(batchId, str) or len(batchId) == 0:
            raise Exception("Invalid message reference for loading scheduled message.")

        # for specified message, category and date definitions are not required
        self.__fromDateTime = None
        self.__toDateTime = None
        self.__batchId = batchId

        # prepare request and submit for response
        scheduledList = self.__loadScheduled()

        if scheduledList is None or scheduledList.getCount() == 0:
            return None

        # there is only one item
        return scheduledList.get(0)

    def __createMessges(self, data: str):
        messagesList = None

        # if the data fragment is empty, then there are no scheduled messages
        if data is None or len(data) == 0:
            return messagesList

        propsReader = MessagePropertiesReader()
        propsReader.setDataFragment(data)
        propsReader.isScheduled(True)

        if self._authProfile is not None:
            propsReader.setAuthProfile(self._authProfile)

        # get and return the messages collection
        return propsReader.getMessages()

    def loadDestinations(self, mc: MessageComposer):
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for loading scheduled destinations.")

        self._setRequestResource("%s/destinations/load/%s" % (ScheduledMessageRequest.__BASE_RESOURCE__, mc.getBatchId()))
        self._setResponseContentType(ContentType.GZBIN_XML)

        # initiailse request writing
        self._initHttpRequest()

        # submit for response
        apiResp = self.submit()
        return MessageComposer.populateScheduledDestinations(mc, apiResp.getDataFragment())

    def cancelSchedule(self, mc: MessageComposer):
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for cancelling scheduled message.")

        # message should be scheduled
        if not mc.isScheduled():
            raise Exception("Message has not been scheduled for cancelling.")

        self._setRequestResource("%s/%s/%s" % (ScheduledMessageRequest.__BASE_RESOURCE__, "cancel", mc.getBatchId()))
        self._initHttpRequest()

        # submit for response
        return self.submit()

    def dispatchMessage(self, mc: MessageComposer):
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for dispatching scheduled message.")

        # message should be a scheduled one
        if not mc.isScheduled():
            raise Exception("Message has not been scheduled for dispatch.")

        self._setRequestResource("%s/dispatch/%s" % (ScheduledMessageRequest.__BASE_RESOURCE__, mc.getBatchId()))
        self._initHttpRequest()

        # submit and return response
        return self.submit()

    def updateMessage(self, mc: MessageComposer):
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for updating scheduled message.")

        self._setRequestResource("%s/%s/%s" % (ScheduledMessageRequest.__BASE_RESOURCE__, "update", mc.getBatchId()))
        self._setResponseContentType(ContentType.GZBIN_XML)

        # initialise request writing
        self._initHttpRequest()
        writer = self._createDataWriter()
        self._requestData = writer.getScheduledMessageUpdateRequestData(mc)

        # submit for response
        msgResp = MessageResponse.create(self.submit())

        # there will be only one message item
        report = msgResp.getReport()
        destsList = report.getDestinations()

        # if new destinations were added, write mode should be refreshed
        if destsList is not None and destsList.getCount() > 0:
            mc.refreshScheduledDestinationsUpdate(destsList)

        # return message response
        return msgResp
