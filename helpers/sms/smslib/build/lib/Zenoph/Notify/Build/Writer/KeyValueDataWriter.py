import abc
from datetime import datetime
from urllib.request import Request

from Zenoph.Notify.Build.Writer.DataWriter import DataWriter
from Zenoph.Notify.Compose.Composer import Composer
from Zenoph.Notify.Compose.SMSComposer import SMSComposer
from Zenoph.Notify.Compose.VoiceComposer import VoiceComposer
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Utils.RequestUtil import RequestUtil
from Zenoph.Notify.Store.PersonalisedValues import PersonalisedValues
from Zenoph.Notify.Collections.ComposerDestinationsList import ComposerDestinationsList

class KeyValueDataWriter(DataWriter):
    __PSND_VALUES_UNIT_SEP__ = "__@"
    __PSND_VALUES_GRP_SEP__ = "__#"
    __DESTINATIONS_SEPARATOR__ = ","

    def __init__(self):
        # parent constructor call
        super().__init__()

        # storage for key values data
        self._keyValueStore: dict = {}

    def getSMSRequestData(self, sc: SMSComposer) ->dict:
        # write message properties
        self.__writeSMSProperties(sc, self._keyValueStore)
        self._writeCommonMessageProperties(sc, self._keyValueStore)

        # write message destinations
        self._writeDestinations(sc, self._keyValueStore)

        # return request data
        return self._prepareRequestData()

    def __writeSMSProperties(self, mc: SMSComposer, store: dict):
        messageText = mc.getMessage()

        self._appendKeyValueData(self._keyValueStore, "text", messageText)
        self._appendKeyValueData(self._keyValueStore, "type", int(mc.getSMSType()))
        self._appendKeyValueData(self._keyValueStore, "sender", mc.getSender())

        # whether message is to be personalised or not
        if SMSComposer.getMessageVariablesCount(messageText) > 0:
            if not mc.personalise():
                self._appendKeyValueData(self._keyValueStore, "personalise", "false")

    #
    # writes voice message request data
    def __writeVoiceMessageProperties(self, vc, store: dict):
        sender = vc.getSender()
        reference = vc.getTemplateReference()

        if sender is not None and len(sender) > 0:
            self._appendKeyValueData(self._keyValueStore, "sender", sender)

        # reference to voice file saved in account
        if reference is not None and len(reference) > 0:
            self._appendKeyValueData(self._keyValueStore, "template", reference)

    def _writeVoiceMessageData(self, vc: VoiceComposer, store: dict):
        # message properties
        self.__writeVoiceMessageProperties(vc, self._keyValueStore)
        self._writeCommonMessageProperties(vc, self._keyValueStore)

        # message destinations
        self._writeDestinations(vc, self._keyValueStore)

    def _writeCommonMessageProperties(self, mc: MessageComposer, store: dict):
        if mc is None:
            raise Exception("Invalid message object reference for writing common message properties.")

        # if message is to be scheduled
        if isinstance(mc, MessageComposer) and mc.schedule():
            scheduleInfo = mc.getScheduleInfo()
            self._writeScheduleInfoData(scheduleInfo[0], scheduleInfo[1], self._keyValueStore)

        # if delivery notifications are requested or not
        if mc.notifyDeliveries():
            callbackInfo = mc.getDeliveryCallback()
            self._writeNotifyInfoData(callbackInfo[0], callbackInfo[1], self._keyValueStore)

    def _writeScheduleInfoData(self, dt: datetime, utcOffset: str, store: dict):
        # validate
        self._validateScheduleInfo(dt, utcOffset)

        # append data
        self._appendKeyValueData(self._keyValueStore, "schedule", RequestUtil.dateTimeToStr(dt))

        # if utc offset is provided, write it
        if utcOffset is not None and len(utcOffset) > 0:
            self._appendKeyValueData(self._keyValueStore, "offset", utcOffset)

    #
    # writes delivery notifications request information data
    def _writeNotifyInfoData(self, url: str, type: ContentType, store: dict):
        # validate
        self._validateDeliveryNotificationInfo(url, type)

        # append data
        self._appendKeyValueData(self._keyValueStore, "callback_url", url)
        self._appendKeyValueData(self._keyValueStore, "callback_accept", RequestUtil.getDataContentTypeLabel(type))

    #
    # writes composer destinations
    def _writeDestinations(self, comp: Composer, store: dict):
        if comp is None or not isinstance(comp, Composer):
            raise Exception("Invalid object reference for writing composer destinations.")

        # get the destinations
        destsList: ComposerDestinationsList = comp.getDestinations()

        if destsList.getCount() == 0:
            raise Exception("There are no items to write message destinations.")

        destsStr = ""
        valueStr = ""

        for compDest in destsList:
            if compDest.getWriteMode() == DestinationMode.DM_NONE:
                continue 

            # get the phone number
            phoneNumber = compDest.getPhoneNumber()

            # if message notifications
            if isinstance(comp, MessageComposer):
                comp.validateDestinationSenderName(phoneNumber)

            # other data
            messageId = compDest.getMessageId()
            destData = compDest.getData()
            tempDestsStr = phoneNumber

            if messageId is not None and len(messageId) > 0:
                tempDestsStr = "%s@%s" % (messageId, phoneNumber)

            if destData is not None and isinstance(destData, PersonalisedValues):
                vals = self.__getPersonalisedValuesStr(destData)

                # append to the personalised values string
                valueStr += ("%s%s" % (KeyValueDataWriter.__PSND_VALUES_GRP_SEP__ if len(valueStr) > 0 else "", vals))

            # append to the destinations
            destsStr += ("%s%s" % (KeyValueDataWriter.__DESTINATIONS_SEPARATOR__ if len(destsStr) > 0 else "", tempDestsStr))

        # append destinations
        self._appendKeyValueData(self._keyValueStore, "to", destsStr)

        # if thre are personalised values, append them too
        if len(valueStr) > 0:
            self._appendKeyValueData(self._keyValueStore, "values", valueStr)

    def __getPersonalisedValuesStr(self, pv: PersonalisedValues) ->str:
        valStr = ""

        for value in pv.export():
            valStr += ("%s%s" % (KeyValueDataWriter.__PSND_VALUES_UNIT_SEP__ if len(valStr) > 0 else "", value))

        # return personalised values string
        return valStr

    def getDestinationsDeliveryRequestData(self, messageIds: list):
        # message Ids
        if messageIds is None or not isinstance(messageIds, list) or len(messageIds) == 0:
            raise Exception("Invalid reference to list for writing destinations delivery request.")

        idsStr = ""

        for messageId in messageIds:
            idsStr += ("%s%s" % (KeyValueDataWriter.__DESTINATIONS_SEPARATOR__ if len(idsStr) > 0 else "", messageId))

        # now append the message Ids
        self._appendKeyValueData(self._keyValueStore, "to", idsStr)

        # return request body string
        return self._prepareRequestData()

    def getDestinationsData(self, comp: Composer) ->dict:
        if comp is None or not isinstance(comp, Composer):
            raise Exception("Invalid composer object reference for writing message destinations.")

        self._writeDestinations(comp, self._keyValueStore)

        # return prepared data
        return self._prepareRequestData()

    def getScheduledMessagesLoadRequestData(self, data: dict):
        # validate
        self._validateScheduledMessagesLoadData(data)

        if "category" in data and data["category"] is not None:
            self._appendKeyValueData(self._keyValueStore, "category", data["category"])

        # date and time specifications
        if "dateFrom" in data and "dateTo" in data:
            self._appendKeyValueData(self._keyValueStore, 'from', RequestUtil.dateTimeToStr(data['dateFrom']))
            self._appendKeyValueData(self._keyValueStore, 'to', RequestUtil.dateTimeToStr(data['dateTo']))

            # if there is UTC offset, append it
            if "offset" in data:
                self._appendKeyValueData(self._keyValueStore, "offset", data["offset"])

        # prepare and return the data
        return self._prepareRequestData()

    def getScheduledMessageUpdateRequestData(self, mc: MessageComposer):
        if mc is None or not isinstance(mc, MessageComposer):
            raise Exception("Invalid message object reference for writing scheduled message update request.")

        # properties to be written will depend on the message category
        if mc.getCategory() == MessageCategory.SMS or mc.getCategory() == MessageCategory.USSD:
            self.__writeSMSProperties(mc, self._keyValueStore)
        else:
            self.__writeVoiceMessageProperties(mc, self._keyValueStore)

        # append message destinations, if any
        if mc.getDestinationsCount() > 0:
            self.__writeScheduledMessageDestinations(mc, self._keyValueStore)

        # prepare and return data
        return self._prepareRequestData()

    def __writeScheduledMessageDestinations(self, mc: MessageComposer, store: dict):
        destsList: ComposerDestinationsList = mc.getDestinations()

        if destsList is None or destsList.getCount() == 0:
            return

        addDestsStr = ""
        addValuesStr = ""
        updateDestsStr = ""
        updateValuesStr = ""
        deleteDestsStr = ""

        for compDest in destsList:
            destMode = compDest.getWriteMode()

            # we are interested in destinations that have been added, updated, or to be deleted
            if destMode == DestinationMode.DM_NONE:
                continue 

            phoneNumber = compDest.getPhoneNumber()
            mc.validateDestinationSenderName(phoneNumber)

            # other data
            destData = compDest.getData()
            messageId = compDest.getMessageId()

            if destMode == DestinationMode.DM_ADD:
                temp = "%s%s" % (phoneNumber, "" if len(messageId) == 0 else ("@%s" % messageId))
                addDestsStr += ("%s%s" % (KeyValueDataWriter.__DESTINATIONS_SEPARATOR__ if len(addDestsStr) > 0 else "", temp))

                # check for personalised values
                if destData is not None and isinstance(destData, PersonalisedValues):
                    valStr = self.__getPersonalisedValuesStr(destData)
                    addValuesStr += ("%s%s" % (KeyValueDataWriter.__PSND_VALUES_GRP_SEP__ if len(addValuesStr) > 0 else "", valStr))

            elif destMode == DestinationMode.DM_UPDATE:
                # the update can be phone number or in the case of SMS, the personalised values
                # so here the main key will be the messageId
                updateDestsStr += ("%s%s%s%s" % (KeyValueDataWriter.__DESTINATIONS_SEPARATOR__ if len(updateDestsStr) > 0 else "", messageId, "@", phoneNumber))

                # check for personalised values
                if destData is not None and isinstance(destData, PersonalisedValues):
                    valStr = self.__getPersonalisedValuesStr(destData)
                    updateValuesStr += ("%s%s" % (KeyValueDataWriter.__PSND_VALUES_GRP_SEP__ if len(updateValuesStr) > 0 else "", valStr))


            elif destMode == DestinationMode.DM_DELETE:
                if messageId is not None and len(messageId) > 0:
                    deleteDestsStr += ("%s%s" % (KeyValueDataWriter.__DESTINATIONS_SEPARATOR__ if len(deleteDestsStr) > 0 else "", messageId))

        # update thos with data
        if len(addDestsStr) > 0:
            self._appendKeyValueData(self._keyValueStore, "to-add", addDestsStr)

            # check for personalised values
            if len(addValuesStr) > 0:
                self._appendKeyValueData(self._keyValueStore, "values-add", addValuesStr)

        # destinations to update
        if len(updateDestsStr) > 0:
            self._appendKeyValueData(self._keyValueStore, "to-update", updateDestsStr)

            # check for personalised values
            if len(updateValuesStr) > 0:
                self._appendKeyValueData(self._keyValueStore, "values-update", updateValuesStr)

        # destinatons do delete
        if len(deleteDestsStr) > 0:
            self._appendKeyValueData(self._keyValueStore, "to-delete", deleteDestsStr)

    def getUSSDRequestData(self, uc):
        pass

    def __writeUSSDData(self, uc, store: dict):
        pass

    #
    #
    def _prepareRequestData(self) ->dict:
        return {"keyValues": self._keyValueStore}

    #
    #
    def _appendKeyValueData(self, store: dict, key: str, value: str):
        store[key] = value
