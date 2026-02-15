from datetime import datetime
from xml.etree import ElementTree

from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Build.Writer.DataWriter import DataWriter
from Zenoph.Notify.Compose.Composer import Composer
from Zenoph.Notify.Compose.SMSComposer import SMSComposer
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Store.PersonalisedValues import PersonalisedValues
from Zenoph.Notify.Utils.RequestUtil import RequestUtil

class XmlDataWriter(DataWriter):
    def __init__(self):
        super().__init__()

    def __createRootElement(self):
        return ElementTree.Element("request")

    def __elementToStr(self, el: ElementTree.Element) ->str:
        return ElementTree.tostring(el, RequestUtil.TEXT_ENCODING_UTF8).decode(RequestUtil.TEXT_ENCODING_UTF8)

    #
    # writes SMS request data
    def getSMSRequestData(self, sc: SMSComposer) ->str:
        rootEl = self.__createRootElement()

        # ensure it is sms object
        if sc is None or not isinstance(sc, SMSComposer):
            raise Exception("Invalid object reference for writing SMS request.")

        # write SMS properties
        self.__writeSMSProperties(sc, rootEl)

        # write message destinations
        self._writeDestinations(sc, rootEl)

        return self.__elementToStr(rootEl)

    #
    # writes SMS message properties
    def __writeSMSProperties(self, sc: SMSComposer, contEl: ElementTree.Element):
        messageText = sc.getMessage()

        # write the message properties
        # message text
        el = ElementTree.SubElement(contEl, "text")
        el.text = messageText

        # message type Id
        el = ElementTree.SubElement(contEl, "type")
        el.text = str(int(sc.getSMSType()))

        # sender Id
        el = ElementTree.SubElement(contEl, "sender")
        el.text = sc.getSender()

        # If there are variables, client can explicitly set personalise flag to false
        if SMSComposer.getMessageVariablesCount(messageText) > 0:
            if not sc.personalise():
                el = ElementTree.SubElement(contEl, "personalise")
                el.text = "false"

        # write common message properties
        self._writeCommonMessageProperties(sc, contEl)

    #
    # writes Voice message request data
    def getVoiceRequestData(self, msgsList: list) ->str:
        if msgsList is None or not isinstance(msgsList, list) or len(msgsList) == 0:
            raise Exception("Invalid object reference for writing voice message request.")

        rootEl = self.__createRootElement()

        

    #
    # writes voice message properties
    def __writeVoiceProperties(self):
        pass

    #
    # writes common message properties
    def _writeCommonMessageProperties(self, mc: MessageComposer, contEl: ElementTree.Element):
        if mc is not None and isinstance(mc, MessageComposer):
            if mc.schedule():
                scheduleInfo: list = mc.getScheduleInfo()
                self._writeScheduleInfo(scheduleInfo[0], scheduleInfo[1], contEl)

            # if delivery notifications are requested
            if mc.notifyDeliveries():
                callbackInfo = mc.getDeliveryCallback()
                self._writeCallbackInfo(callbackInfo[0], callbackInfo[1], contEl)

    #
    # writes message destinations
    def _writeDestinations(self, mc, contEl: ElementTree.Element):
        destsList = mc.getDestinations()

        # it should not be empty
        if destsList.getCount() == 0:
            raise Exception("There are no message destinations to send SMS request.")

        destsEl = ElementTree.SubElement(contEl, "destinations")

        for compDest in destsList:
            if compDest.getWriteMode() == DestinationMode.DM_NONE:
                continue 

            phoneNumber = compDest.getPhoneNumber()

            # if it is a message composer, check sender Id
            if isinstance(mc, MessageComposer):
                mc.validateDestinationSenderName(phoneNumber)

            # get other values for writing
            messageId = compDest.getMessageId()
            destData = compDest.getData()

            # write destination item
            self.__writeDestinationItem(phoneNumber, messageId, destData, destsEl)

    #
    # writes destination item
    def __writeDestinationItem(self, phoneNumber: str, messageId: str, destData: object, contEl: ElementTree.Element):
        if messageId is None and destData is None:
            el = ElementTree.SubElement(contEl, "to")
            el.text = phoneNumber
        else:
            self.__writeDestinationWithData(phoneNumber, messageId, destData, contEl)

    #
    # writes destination info
    def __writeDestinationWithData(self, phoneNumber: str, messageId: str, destData: object, contEl: ElementTree.Element):
        # if phone number provided, then write it
        if phoneNumber is not None and len(phoneNumber) > 0:
            toEl = ElementTree.SubElement(contEl, "to")
            numEl = ElementTree.SubElement(toEl, "number")
            numEl.text = phoneNumber

        # message Id
        if messageId is not None and len(messageId) > 0:
            msgIdEl = ElementTree.SubElement(toEl, "id")
            msgIdEl.text = messageId

        # if there are personalised values
        if destData is not None and isinstance(destData, PersonalisedValues):
            self.__writeDestinationPersonalisedValues(destData, toEl)

    #
    # writes persoalised values for destination
    def __writeDestinationPersonalisedValues(self, pv: PersonalisedValues, contEl: ElementTree.Element):
        valuesEl = ElementTree.SubElement(contEl, "values")

        for value in pv.export():
            valEl = ElementTree.SubElement(valuesEl, "value")
            valEl.text = str(value)

    #
    # writes message scheduling information
    def _writeScheduleInfo(self, dateTime: datetime, offset: str, contEl: ElementTree.Element):
        self._validateScheduleInfo(dateTime, offset)

        schedEl = ElementTree.SubElement(contEl, "schedule")
        
        # date and time
        el = ElementTree.SubElement(schedEl, "dateTime")
        el.text = RequestUtil.dateTimeToStr(dateTime)

        # utc offset is optionl. check if there it is set
        if offset is not None and len(offset) > 0:
            el = ElementTree.SubElement(schedEl, "offset")
            el.text = offset

    #
    # writes delivery notification information
    def _writeCallbackInfo(self, url: str, contentType: ContentType, contEl: ElementTree.Element):
        # validate
        self._validateDeliveryNotificationInfo(url, contentType)

        notifyEl = ElementTree.SubElement(contEl, "callback")
        el = ElementTree.SubElement(notifyEl, "url")
        el.text = url

        # content type label
        el = ElementTree.SubElement(notifyEl, "accept")
        el.text = RequestUtil.getDataContentTypeLabel(contentType)

    #
    # writes message destinations data
    def getDestinationsData(self, mc: Composer) ->str:
        if mc is None or not isinstance(mc, Composer):
            raise Exception("Invalid object reference for writing request destinations.")

        rootEl = ElementTree.Element("request")

        # write destinations
        self._writeDestinations(mc, rootEl)

        # convert to string and return it
        return self.__elementToStr(rootEl)

    #
    # writes destinations delivery request data
    def getDestinationsDeliveryRequestData(self, messageIds: list) ->str:
        if messageIds is None or not isinstance(messageIds, list) or len(messageIds) == 0:
            raise Exception("There are no message identifiers for writing destinations delivery request.")

        rootEl = self.__createRootElement()

        # write message Ids
        destsEl = ElementTree.SubElement(rootEl)

        for messageId in messageIds:
            if messageId is not None and len(messageId) > 0:
                el = ElementTree.SubElement(destsEl, "id")
                el.text = messageId

        # convert to string and return
        return self.__elementToStr(rootEl)

    #
    # writes scheduled messages load request data
    def getScheduledMessagesLoadRequestData(self, filter: dict):
        self._validateScheduledMessagesLoadData(filter)

        rootEl = self.__createRootElement()

        # if a message reference is specified, then it means that
        # we are to load a specific scheduled message

        if "batch" in filter:
            self.__writeMessageBatchId(filter["batch"], rootEl)
        else:
            if "category" in filter:
                el = ElementTree.SubElement(rootEl, "category")
                el.text = str(int(filter["category"]))

            # check to see if there are dates specified
            if "dateFrom" in filter and "dateTo" in filter and filter["dateFrom"] is not None and filter["dateTo"] is not None:
                dtEl = ElementTree.SubElement(rootEl, "dateTime")
                
                # date from
                el = ElementTree.SubElement(dtEl, "from")
                el.text = RequestUtil.dateTimeToStr(filter["dateFrom"])

                # date to
                el = ElementTree.SubElement(dtEl, "to")
                el.text = RequestUtil.dateTimeToStr(filter["dateTo"])

                # UTC offset is optional. check to see if it is specified
                if "utcOffset" in filter:
                    el = ElementTree.SubElement(dtEl, "offset")
                    el.text = filter["offset"]

        # convert element to string and return
        return self.__elementToStr(rootEl)

    #
    # writes scheduled message update request
    def getScheduledMessageUpdateRequestData(self, mc: MessageComposer) ->str:
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for writing scheduled message update request.")

        rootEl = self.__createRootElement()
        category = mc.getCategory()

        # write message reference
        # self.__writeMessageBatchId(mc.getReferenceId(), rootEl)

        if category == MessageCategory.SMS:
            self.__writeSMSProperties(mc, rootEl)
        elif category == MessageCategory.VOICE:
            self.__writeVoiceProperties(mc, rootEl)

        # if there are destinations to be written
        if mc.getDestinationsCount() > 0:
            self.__writeScheduledMessageDestinations(mc, rootEl)

        # convert to string and return it
        return self.__elementToStr(rootEl)

    #
    # writes scheduled message destinations data
    def __writeScheduledMessageDestinations(self, mc: MessageComposer, contEl: ElementTree.Element):
        # get destinations
        destsList = mc.getDestinations()

        if destsList is None or destsList.getCount() == 0:
            return

        addEl = None # ElementTree.Element("add")
        updateEl = None # ElementTree.Element("update")
        deleteEl = None # ElementTree.Element("delete")

        for destInfo in destsList:
            destMode = destInfo.getWriteMode()

            # if destination is NONE, we will not write
            if destMode == DestinationMode.DM_NONE:
                continue 

            phoneNumber = destInfo.getPhoneNumber()
            mc.validateDestinationSenderName(phoneNumber)

            # other values
            destData = destInfo.getData()
            messageId = destInfo.getMessageId()

            if destMode == DestinationMode.DM_ADD:
                if addEl is None:
                    addEl = ElementTree.Element("add")
                self.__writeDestinationItem(phoneNumber, messageId, destData, addEl)

            elif destMode == DestinationMode.DM_UPDATE:
                if updateEl is None:
                    updateEl = ElementTree.SubElement("update")
                self.__writeDestinationItem(phoneNumber, messageId, destData, updateEl)

            elif destMode == DestinationMode.DM_DELETE:
                if deleteEl is None:
                    deleteEl = ElementTree.SubElement("delete")
                self.__writeDestinationItem(None, messageId, None, deleteEl)

        destsEl = ElementTree.SubElement(contEl, "destinations")

        # insert into the main element
        if addEl is not None:
            destsEl.append(addEl)

        # destination updates
        if updateEl is not None:
            destsEl.append(updateEl)

        # destinations to be deleted
        if deleteEl is not None:
            destsEl.append(deleteEl)

    #
    # writes USSD request data
    def getUSSDRequestData(self, c):
        pass

    #
    # writes message reference id
    def __writeMessageBatchId(self, batchId: str, contEl: ElementTree.Element):
        el = ElementTree.SubElement(contEl, "batch")
        el.text = batchId