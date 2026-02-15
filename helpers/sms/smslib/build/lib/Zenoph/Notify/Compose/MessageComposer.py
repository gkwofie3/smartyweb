import uuid
from abc import ABC
from xml.dom import pulldom

from Zenoph.Notify.Compose.IMessageComposer import IMessageComposer
from Zenoph.Notify.Compose.Composer import Composer
from Zenoph.Notify.Compose.ISchedule import ISchedule
from Zenoph.Notify.Compose.Schedule import Schedule
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Enums.DestinationStatus import DestinationStatus
from Zenoph.Notify.Store.MessageDestination import MessageDestination
from Zenoph.Notify.Collections.MessageDestinationsList import MessageDestinationsList
from Zenoph.Notify.Build.Reader.MessageDestinationsReader import MessageDestinationsReader
from Zenoph.Notify.Utils.XMLUtil import XMLUtil

class MessageComposer(Composer, IMessageComposer, ISchedule):
    def __init__(self, authProfile = None):
        super().__init__(authProfile)

        self._sender: str = None
        self._message: str = None
        self._scheduler: Schedule = Schedule()
        self._batchId: str = None
        self._isScheduled: bool = False
        self._delivCallbackURL = None
        self._delivCallbackAccept = ContentType.XML

    def getSender(self):
        return self._sender

    # sets the message sender Id
    def setSender(self, sender):
        if sender == None or sender == "":
            raise Exception('Missing or invalid message sender identifier.')

        # set the sender id 
        self._sender = sender


    #
    # sets a message
    def setMessage(self, message: str, extData = None):
        if message is None or message == "":
            raise Exception("Invalid message text or reference.")

        # set the message
        self._message = message

    #
    # gets the message
    def getMessage(self):
        return self._message


    def getBatchId(self):
        return self._batchId

    def getScheduleInfo(self):
        return [self._scheduler.getDateTime(), self._scheduler.getUTCOffset()]

    #
    # checks if messageId exists
    def messageIdExists(self, messageId: str) ->bool:
        return self.destinationIdExists(messageId);

    #
    # gets messageId for specified phone number
    def getMessageId(self, phoneNumber: str) ->str:
        if phoneNumber is None or phoneNumber == "":
            raise Exception("Invalid phone number for destination message identifier.")

        # destination should exist
        if not self.destinationExists(phoneNumber):
            raise Exception(f"Phone number '{phoneNumber}' does not exist in the destinations list.")

        numberInfo = self._formatPhoneNumber(phoneNumber)
        fmtdNumber = numberInfo[Composer.__PHONE_NUMBER_LABEL__]

        if not self._formattedDestinationExists(fmtdNumber):
            raise Exception(f"Destination '{phoneNumber}' does not exist in the message destinations list.")

        # get the destinatons list for this particular phone number
        compDestList = self._getMappedDestinations(fmtdNumber)

        # we don't expect multiple items
        if len(compDestList) > 1:
            raise Exception(f"There are multiple composer destinations for phone number '{fmtdNumber}'.")

        # return messageId
        return compDestList[0].getMessageId()

    #
    # sets URL for delivery notifications
    def setDeliveryCallback(self, url: str, contentType: ContentType):
        if url is None or len(url.strip()) == 0:
            self._delivCallbackURL = None
            return 

        # we will not accept compressed formats for the content type
        if contentType != ContentType.XML and contentType != ContentType.JSON:
            raise Exception("Invalid data content type specifier for delivery status notifications.")

        self._delivCallbackURL = url
        self._delivCallbackAccept = contentType


     #
    # gets notify URL info
    def getDeliveryCallback(self):
        return [self._delivCallbackURL, self._delivCallbackAccept]


    def notifyDeliveries(self) ->bool:
        return True if self._delivCallbackURL is not None and len(self._delivCallbackURL.strip()) > 0 else False


    # indicates whether message was scheduled or not
    def isScheduled(self) ->bool:
        return self._isScheduled

    # checks whether will be scheduled or not
    def schedule(self) ->bool:
        return not self._scheduler.getDateTime() is None

    # creates composer destination object
    def _createComposerDestination(self, phoneNumber: str, messageId: str, destMode: DestinationMode, destData, isScheduled: bool = False):
        # for scheduled messages that have been loaded, we will automatically assign a
        # message Id if client does not provide one
        if self.isScheduled() and (messageId is None or messageId == ""):
            messageId = self.__generateMessageId()

        return super()._createComposerDestination(phoneNumber, messageId, destMode, destData, isScheduled)

    # generates a message Id
    def __generateMessageId(self) ->str:
        messageId: str = None
        exists: bool = True

        while exists == True:
            messageId = str(uuid.uuid4())
            exists = True if messageId in self._destIdsMap else False

        return messageId

    # populates scheduled message destinations
    @staticmethod
    def populateScheduledDestinations(mc, data: object) ->int:
        if mc is None:
            raise Exception("Invalid message composer object for populating scheduled destinations.")

        # the message should be a scheduled one
        if not mc.isScheduled():
            raise Exception("Message has not been scheduled for populating destinations.")

        if data is None or isinstance(data, str) == False or len(data) == 0:
            raise Exception("Invalid data for populating scheduled message destinations.")

        # clear any existing destinations
        mc.clearDestinations()

        # read and return destinations count
        return MessageComposer.__readScheduledDestinations(mc, data)

    # reads scheduled destinations
    @staticmethod
    def __readScheduledDestinations(mc, data: object) ->int:
        reader = MessageDestinationsReader()
        reader.setData(XMLUtil.createXMLDocument(data))
        count = 0

        while True:
            md: MessageDestination = reader.getNextItem()

            if md is None:
                break

            phoneNumber = md.getPhoneNumber()
            messageId = md.getMessageId()
            destData = md.getData()
            destMode = DestinationMode.DM_NONE
            scheduled = True

            # create composer destination object
            compDest = mc._createComposerDestination(phoneNumber, messageId, destMode, destData, scheduled)
            countryCode = mc._getDestinationCountryCode(phoneNumber)

            # add to destinations list and increment count
            mc._addComposerDestination(compDest, countryCode)
            count += 1

        # return total destinations
        return count


    # sets date and time for scheduling message
    def setScheduleDateTime(self, dateTime, val1 = None, val2 = None):
        self._scheduler.setScheduleDateTime(dateTime, val1, val2)

    # removes message destination object
    def __removeMessageDestination(self, md: MessageDestination) ->bool:
        # removal of object of this type is only allowed on scheduled message destinations
        if not self.isScheduled():
            raise Exception("Message destination objects can only be removed from loaded scheduled messages.")

        messageId = md.getMessageId()

        # the message Id should exist
        if messageId in self._destIdsMap:
            compDest = self._getComposerDestinationById(messageId)

            if compDest is not None:
                return self._removeComposerDestination(compDest)

        # nothing removed at this point
        return False

    # removes message destination for specified messageId
    def removeDestinationById(self, messageId: str) ->bool:
        # if the message is not a scheduled one that has been loaded, then call parent to remove
        if not self.isScheduled():
            return super().removeDestinationById(messageId)
        else:
            # message is a scheduled one which has been loaded. we will only change the
            # write mode so that it will be removed on the server. but first ensure the id exists
            if self.messageIdExists(messageId):
                compDest = self._getComposerDestinationById(messageId)
                replCompDest = None

                # Though message is scheduled, it is possible for destination to be non-scheduled
                # if it was newly added after the scheduled message was loaded
                if compDest.isScheduled():
                    destMode = DestinationMode.DM_DELETE
                    replCompDest = self._createComposerDestination(None, messageId, destMode, None, True)

                # remove destination
                self._removeComposerDestination(compDest)

                # if scheduled destination to be removed, replCompDest will not be None
                if replCompDest is not None:
                    self._addComposerDestination(replCompDest)

                # return success
                return True
            else:
                return False

    # updates destination phone number for specified messageId
    def updateDestinationById(self, messageId: str, phoneNumber: str) ->bool:
        if not self.isScheduled():
            return super().updateDestinationById(messageId, phoneNumber)
        else:
            if phoneNumber is None or len(phoneNumber) == 0:
                raise Exception("Invalid phone number for updating message destination.")

            numberInfo = self._formatPhoneNumber(phoneNumber, True)
            fmtdNumber = numberInfo[MessageComposer.__PHONE_NUMBER_LABEL__]
            countryCode = numberInfo[MessageComposer.__DEST_COUNTRYCODE_LABEL__]

            if self.messageIdExists(messageId):
                return self._updateComposerDestination(self._getComposerDestinationById(messageId), fmtdNumber)
            else:
                destMode = DestinationMode.DM_UPDATE
                compDest = self._createComposerDestination(fmtdNumber, messageId, destMode, None, True)

                # add for update
                self._addComposerDestination(compDest, countryCode)
                return True

    # refresh scheduled destinations that where loaded
    def refreshScheduledDestinationsUpdate(self, destsList: list):
        if destsList is None:
            raise Exception("Invalid object reference to message destinations.")

        # this message should be a scheduled one
        if not self.isScheduled():
            raise Exception("The message has not been scheduled for refreshing updated destinations.")

        for mDest in destsList:
             if mDest.getStatus() == DestinationStatus.DS_SCHEDULE_DELETED:
                 self.__removeMessageDestination(mDest)
             else:
                 self.__resetScheduledDestination(mDest.getMessageId())

    #
    # resets scheduled destinations
    def __resetScheduledDestination(self, messageId: str):
        if messageId is None or len(messageId) == 0:
            raise Exception("Invalid message identifier for resetting destination write mode.")

        # the message id should exist
        if not self.messageIdExists(messageId):
            raise Exception("Message identifier '%s' does not exist." % messageId)

        # we will have to replace it. get the original one
        prevCompDest = self._getComposerDestinationById(messageId)
        phoneNumber = prevCompDest.getPhoneNumber()
        destMode = DestinationMode.DM_NONE
        data = prevCompDest.getData()

        # create new one for replacement
        newCompDest = self._createComposerDestination(phoneNumber, messageId, destMode, data, True)
        countryCode = self._getDestinationCountryCode(phoneNumber)

        # remove and replace
        self._removeComposerDestination(prevCompDest)
        self._addComposerDestination(newCompDest, countryCode)

    # validates destination for update
    def _validateDestinationUpdate(self, prevPhoneNumber: str, newPhoneNumber: str):
        if prevPhoneNumber is None or len(prevPhoneNumber) == 0:
            raise Exception("Invalid object reference to previous phone number for updating destination.")

        if newPhoneNumber is None or len(newPhoneNumber) == 0:
            raise Exception("Invalid object reference to new phone number for updating destination.")

        # convert to international format
        preNumInfo: dict = self._formatPhoneNumber(prevPhoneNumber)
        newNumInfo: dict = self._formatPhoneNumber(newPhoneNumber)

        if preNumInfo is None:
            raise Exception("Invalid or unsupported previous phone number for updating destination.")

        if newNumInfo is None:
            raise Exception("Invalid or unsupported new phone number for updating destination.")

        # if not scheduled message that has been loaded, thenwe will have to validate the phone numbers
        if not self.isScheduled():
            # previous phone number should exist in the destinations list
            if not self._formattedDestinationExists(preNumInfo[MessageComposer.__PHONE_NUMBER_LABEL__]):
                raise Exception("Phone number '%s' does not exist." % prevPhoneNumber)

            # the new number should not already exist
            if self._formattedDestinationExists(newNumInfo[MessageComposer.__PHONE_NUMBER_LABEL__]):
                raise Exception("Phone number '%s' already exists." % newPhoneNumber)

        return {"pre": preNumInfo, "new": newNumInfo}

    # validates sender Id for destination in message
    def validateDestinationSenderName(self, phoneNumber: str):
        # the phone number must exist
        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            return

        fmtdNumber = numberInfo[MessageComposer.__PHONE_NUMBER_LABEL__]

        if self._userData is None or not self._formattedDestinationExists(fmtdNumber):
            return

        # get the country code and find outif the country requires sender registration or not
        countryCode = self._destNumbersMap[fmtdNumber][MessageComposer.__DEST_COUNTRYCODE_LABEL__]
        routeFilters: dict = self._userData.getRouteFilters()

        if countryCode is not None and len(countryCode) > 0 and countryCode in routeFilters:
            countryName = routeFilters[countryCode]["countryName"]

            # see if sender registration is required and then take ncessary step
            if routeFilters[countryCode]["registerSender"] == True:
                self.__checkSenderRegistration(countryCode, countryName)

            # see if numeric sender is allowed in case message sender id is numeric
            if MessageUtil.isNumericSender(self._sender) and not routeFilters[countryCode]["numericSenderAllowed"]:
                raise Exception("Numeric sender Id is not allowed in sending messages to '%s'." % countryName)

    # checks sender name registration requirement
    def __checkSenderRegistration(self, countryCode: str, countryName: str):
        # get message sender Ids
        senders = self._userData.getMessageSenders()
        categoryLabel = MessageUtil.getMessageCategoryLabel(self._category)
        senderMatched = False

        if senders is None or not categoryLabel in senders:
            raise Exception("Message sender Id '%s' is not permitted for sending messages to '%s'." % (self._sender, countryName))

        categorySenderIds: dict = senders[categoryLabel]

        for senderName in categorySenderIds:
            caseSensitive: bool = categorySenderIds[senderName]["sensitive"]
            countryCodes: list = categorySenderIds[senderName]["countryCodes"]

            # see if there is a match, then we check country codes
            if self.__isMessageSenderMatch(senderName, caseSensitive):
                # find out if sender id is permitted in the specified country
                if not self.__senderCountryCodeExists(countryCodes, countryCode):
                    continue 

                # we found match
                senderMatched = True
                break

        # if not match, raise Exception
        if not senderMatched:
            raise Exception("Message sender Id '%s' is not permitted for sending messages to '%s'." % (self._sender, countryName))

    # checks whether sender Id is approved for country or not
    def __senderCountryCodeExists(self, countryCodes: list, testCode: str) ->bool:
        for code in countryCodes:
            if code.lower() == testCode.lower():
                return True

        # not matched
        return False

    def __isMessageSenderMatch(self, testSenderId, isCaseSensitive: bool) ->bool:
        if isCaseSensitive == True:
            return True if self._sender == testSenderId else False
        else:
            return True if self._sender.lower() == testSenderId.lower() else False