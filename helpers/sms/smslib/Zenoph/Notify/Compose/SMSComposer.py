#from Zenoph.Notify.Compose import ISMSComposer, MessageComposer
#from Zenoph.Notify.Enums import TextMessageType, MessageCategory, NumberAddInfo, DestinationMode
#from Zenoph.Notify.Store import AuthProfile

import re

from Zenoph.Notify.Collections.PersonalisedValuesList import PersonalisedValuesList
from Zenoph.Notify.Compose.ISMSComposer import ISMSComposer
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Enums.SMSType import SMSType
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Enums.NumberAddInfo import NumberAddInfo
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Store.PersonalisedValues import PersonalisedValues
from Zenoph.Notify.Store.ComposerDestination import ComposerDestination
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Utils.PhoneUtil import PhoneUtil
from Zenoph.Notify.Utils.MessageUtil import MessageUtil

class SMSComposer(MessageComposer, ISMSComposer):
    __NUMERIC_SENDER_MAX_LEN__ = 18;
    __ALPHA_NUMERIC_SENDER_MAX_LEN__ = 11
    __VARIABLES_PATTERN__ = "\{\\$[a-zA-Z_][a-zA-Z0-9]+\}"

    # constructor
    def __init__(self, ap: AuthProfile = None):
        super().__init__(ap)
        
        self.__type = SMSType.GSM_DEFAULT
        self.__personalise = False
        self._category = MessageCategory.SMS

        if ap is not None and isinstance(ap, AuthProfile):
            self.__type = ap.getUserData().getDefaultTextMessageType()

    # static create method
    @staticmethod
    def create(data:  dict):
        if data is None or not isinstance(data, dict):
            raise Exception("Invalid data for initialising SMS composer.")

        ap: AuthProfile = None
        batchId: str = None
        scheduled: bool = False

        if "authProfile" in data:
            ap = data["authProfile"]

            # we do not expect it to be None since it was explicitly set
            if ap is None or isinstance(ap, AuthProfile) == False:
                raise Exception("Invalid authentication profile reference for initialising SMS composer.")

        # check for message reference id (templateId)
        if "batch" in data:
            batchId = data["batch"]

            # we do not expect it to be None since it was explicitly set
            if batchId is None or len(batchId) == 0:
                raise Exception("Invalid message batch identifier for initialising SMS composer.")

            # we expect message category as well
            if not "category" in data:
                raise Exception("Missing message category specifier for initialising SMS composer.")

        # initialise SMS composer
        sc = SMSComposer() if ap is None else SMSComposer(ap)

        # check if it is a scheduled message which was loaded
        if "scheduled" in data and isinstance(data["scheduled"], bool):
            scheduled = data["scheduled"]

        if batchId is not None and len(batchId) > 0:
            sc._batchId = batchId
            sc._category = data["category"]

        # schedule state
        sc._isScheduled = scheduled

        # return initialised SMS composer
        return sc

    @staticmethod
    def getMessageCount(message: str, type: SMSType) ->int:
        if message is None or len(message) == 0:
            return 0

        if type is None or isinstance(type, SMSType) == False:
            raise Exception("Invalid message type specifier for determining message count.")

        typeInfo = MessageUtil.getMessageTypeInfo(type)

        # determine the message count
        messageLen = len(message)
        splitSize = typeInfo["concatLen"] if messageLen > typeInfo["singleLen"] else typeInfo["singleLen"]
        remCount = messageLen
        messageCount = 1

        while remCount > splitSize:
            messageCount += 1
            remCount -= splitSize

        # return message count
        return messageCount

    @staticmethod
    def getMessageVariablesCount(message: str) ->int:
        if message is None or len(message) == 0:
            return 0

        return len(SMSComposer.getMessageVariables(message))

    @staticmethod
    def getMessageVariables(message: str, trim: bool = True) ->list:
        varsList = []
        matches = re.findall(SMSComposer.__VARIABLES_PATTERN__, message)

        if matches is not None:
            for match in matches:
                if trim:
                    match = SMSComposer.__trimVariable(match)

                # add to variables list
                varsList.append(match)

        # return variables
        return varsList

    #
    # trims variables found in message text
    @staticmethod
    def __trimVariable(variable: str) ->str:
        return re.sub("[\{\}\$]", "", variable)

    #
    # gets the sms sender Ids
    def getRegisteredSenderIds(self) ->list:
        if self._userData is None:
            return None

        sendersInfo = self._userData.getMessageSenders()
        smsCategoryLabel = MessageUtil.getMessageCategoryLabel(MessageCategory.SMS)

        if sendersInfo is None or len(sendersInfo) == 0 or not smsCategoryLabel in sendersInfo:
            return None

        # extract and return the sender Ids
        return self.__extractSenderIds(sendersInfo[smsCategoryLabel])

    #
    # extracts and returns message senderIds
    def __extractSenderIds(self, sendersMap: dict) ->list:
        senderIds = []

        for sender in sendersMap:
            senderIds.append(sender)

        return senderIds

    #
    # whether message is to be personalised or not
    def personalise(self) ->bool:
        return self.__personalise

    #
    # checks that personalised values are Ok
    def __assertPersonalisedValues(self, phoneNumber: str, values: list, throwEx: bool) ->NumberAddInfo:
        if values is None or isinstance(values, list) == False or len(values) == 0:
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_VALUES_EMPTY

            # rais exception
            raise Exception("Invalid reference to personalised values data.")

        # the message text should have already been set
        if self._message is None or len(self._message) == 0:
            # here, we will raise exception irrespective of throwEx
            raise Exception("Message text has not been set for validating personalised values.")

        # variables defined
        varsList = SMSComposer.getMessageVariables(self._message)

        if varsList is None or len(varsList) != len(values):
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_VALUES_COUNT

            # raise exception
            raise Exception("Mismatch variables and values count.")

        # all values must be provided
        valPos = 0

        for val in values:
            valPos += 1

            if val is None:
                if not throwEx:
                    return NumberAddInfo.NAI_REJTD_VALUES_MISVAL
                else:
                    raise Exception("Invalid personalised value at position '%d' for phone number '%s'." % (valPos, phoneNumber))

        # all is well
        return NumberAddInfo.NAI_OK

    #
    # adds a personalised destination with values
    def addPersonalisedDestination(self, phoneNumber: str, throwEx: bool, values: list, messageId: str = None) ->NumberAddInfo:
        if phoneNumber is None or len(phoneNumber) == 0 or not PhoneUtil.isValidPhoneNumber(phoneNumber):
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_INVALID
            else:
                raise Exception("Invalid phone number for adding personalised message values.")

        # the message text should be set as being personalised
        if not self.personalise():
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_NON_PSND
            else:
                raise Exception("Message is not set to be personalised for adding values.")

        numberAddInfo = None

        # if message Id is provided, it should be validated
        if messageId is not None and len(messageId) > 0:
            numberAddInfo = self._validateCustomMessageId(messageId, throwEx)

            if numberAddInfo != NumberAddInfo.NAI_OK:
                return numberAddInfo

        # also validate the personalised values
        numberAddInfo = self.__assertPersonalisedValues(phoneNumber, values, throwEx)

        if numberAddInfo != NumberAddInfo.NAI_OK:
            return numberAddInfo

        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_ROUTE
            else:
                raise Exception("Phone number '%s is invalid or not permitted on registered routes." % phoneNumber)

        fmtdNumber = numberInfo[MessageComposer.__PHONE_NUMBER_LABEL__]
        countryCode = numberInfo[MessageComposer.__DEST_COUNTRYCODE_LABEL__]
        valuesContainer: PersonalisedValuesList = self.__getDestinationPersonalisedValues(fmtdNumber)

        # we will not allow same set of values for the same destination phone number
        if valuesContainer is not None and self.__valuesExist(valuesContainer, values):
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_VALUES_EXIST
            else:
                raise Exception("Personalised values already exist for destination '%s'." % phoneNumber)

        pv = PersonalisedValues(values)
        return self._addDestinationInfo(fmtdNumber, countryCode, messageId, pv)

    #
    # gets Id of personalised message
    def getPersonalisedMessageId(self, phoneNumber: str, values: list) ->str:
        if not self.personalise():
            return super().getMessageId(phoneNumber)
        else:
            # values must be provided
            if values is None or len(values) == 0:
                raise Exception("Invalid reference to values list for custom message identifier.")

            # get the composer destinations list
            compDestsList: list = self._getMappedDestinations(self._getFormattedPhoneNumber(phoneNumber))

            for destInfo in compDestsList:
                # get the personalised values and check if we have it
                pv = destInfo.getData()

                if ",".join(pv.export()) == ",".join(values):
                    return destInfo.getMessageId()

            # not found
            raise Exception("The specified personalised values were not found.")
    #
    # adds specified phone number to message destinations
    def addDestination(self, phoneNumber: str, throwEx: bool = True, messageId: str = None):
        if self._message is not None and len(self._message) != 0:
            if SMSComposer.getMessageVariablesCount(self._message) > 0 and self.personalise():
                if not throwEx:
                    return NumberAddInfo.NAI_REJTD_VALUES_EMPTY

                raise Exception("Missing personalised values for destination.")

        return super().addDestination(phoneNumber, throwEx, messageId)

    # checks to see if personalised values exist
    def __valuesExist(self, pvList: PersonalisedValuesList, values: list) ->bool:
        if pvList is not None:
            for pv in pvList:
                if ",".join(pv.export()) == ",".join(values):
                    return True

        # not found
        return False

    # checks to see if personalised values exist (this is called publicly)
    def personalisedValuesExists(self, phoneNumber: str, values) ->bool:
        if phoneNumber is None or len(phoneNumber) == 0:
            raise Exception("Invalid phone number for verifying personalised values.")

        # if phon number does not exist, then values do not exist
        if not self.destinationExists(phoneNumber):
            return False

        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)

        # assert the personalised values
        self.__assertPersonalisedValues(fmtdNumber, values, True)

        # get the personalised values and check
        return self.__valuesExist(self.getPersonalisedValues(fmtdNumber), values)

    # remove personalised destination
    def removePersonalisedDestination(self, phoneNumber: str, values: list) ->bool:
        if phoneNumber is None or len(phoneNumber) == 0:
            raise Exception("Invalid phone number for removing personalised message destination.")

        if values is None or isinstance(values, list) == False or len(values) == 0:
            raise Exception("Invalid values for removing personalised message destination.")

        # destination should exist
        if not self.destinationExists(phoneNumber):
            raise Exception("Phone number '%s' does not exist." % phoneNumber)

        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)
        compDestsList: list = self._getMappedDestinations(fmtdNumber)

        for compDest in compDestsList:
            pv = compDest.getData()

            # export the values as list of string and compare with the list passed to this call
            if ",".join(pv.export()) == ",".join(values):
                return self._removeComposerDestination(compDest)

        # nothing removed
        return False
        

    # removes values for destination in personalised messaging
    def removePersonalisedValues(self, phoneNumber: str, values: list) ->bool:
        if phoneNumber is None or len(phoneNumber) == 0:
            raise Exception("Invalid phone number for removing personalised values.")

        if values is None or isinstance(values, list) == False or len(values) == 0:
            raise Exception("Invalid reference data for removing personalised values.")

        # ensure the destination exists
        if not self.destinationExists(phoneNumber):
            return False

        # message should be a personalised one
        if not self.personalise():
            raise Exception("Message has not been personalised for removing values.")

        # we should get the values and remove
        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)
        compDestsList: list = self._getMappedDestinations(fmtdNumber)
        countryCode: str = self._getDestinationCountryCode(fmtdNumber)

        # if there is only one set of values, we will not allow delete on it since it will 
        # leave the destination phone number without personalised values. If client wants the
        # phone number with its values to be deleted, them, 'removePersonalisedDestination()' should be called instead
        if len(compDestsList) == 0:
            raise Exception("Cannot remove single set personalised values for destination.")

        for compDest in compDestsList:
            pv: PersonalisedValues = compDest.getData()

            if ",".join(pv.export()) == ",".join(values):
                # for messages that were scheduled and loaded, we will change the write mode and
                # replace back so that when sent to the server, the destination will be removed
                replCompDest: ComposerDestination = None

                if compDest.isScheduled():
                    # the only way to change write mode is to create new one with DELETE write mode and remove existing one
                    messageId = compDest.getMessageId()
                    destMode = DestinationMode.DM_DELETE

                    # create new one for replacement
                    replCompDest = self._createComposerDestination(fmtdNumber, messageId, destMode, pv, True)
                
                # remove the existing one we found
                self._removeComposerDestination(compDest)

                # if scheduled destination which was loaded, then we should add its replacement
                if replCompDest is not None:
                    self._addComposerDestination(replCompDest, countryCode)

                # removed, so return success
                return True

        # nothing removed
        return False

    # gets the default text message type for the account
    def getDefaultSMSType(self) ->SMSType:
        if self._userData is None:
            return None

        return self._userData.getDefaultTextMessageType()

    # get the write mode for personalised destination. That is, whether it should be updated, deleted, or inserted as new
    def getPersonalisedDestinationWriteMode(self, phoneNumber: str, values) ->DestinationMode:
        # message should be set to be personalised
        if not self.personalise():
            raise Exception("Message is not set to be personalised for destination mode.")

        # destination should already exists
        if not self.destinationExists(phoneNumber):
            raise Exception("Phone number '%s' does not exist." % phoneNumber)

        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)
        compDestsList = self._getMappedDestinations(fmtdNumber)

        for compDest in compDestsList:
            if self.__valuesMatch(compDest.getData().export(), values):
                return compDest.getWriteMode()

        # at this point the values were not found
        raise Exception("The specified personalised values were not found for the destination phone number.")

    #
    # get messageId associated with a personalised message
    def getPersonalisedDestinationMessageId(self, phoneNumber: str, values: list) ->str:
        if not self.personalise():
            return super().getMessageId(phoneNumber)
        else:
            # values must be provided
            if values is None or isinstance(values, list) == False or len(values) == 0:
                raise Exception("Invalid reference to values list for custom message identifier.")

            compDestsList = self._getMappedDestinations(self._getFormattedPhoneNumber(phoneNumber))

            for compDest in compDestsList:
                if self.__valuesMatch(compDest.getData().export(), values):
                    return compDest.getMessageId

        # not found
        raise Exception("The specified personalised values were not found for the destination.")

    #
    # checks to see if list values match
    def __valuesMatch(self, val1: list, val2: list) ->bool:
        return ",".join(val1) == ",".join(val2)

    #
    # get the personalised values for a destination phone number. This is intented to be called privately 
    # It first converts the phone number into international number format
    def __getDestinationPersonalisedValues(self, phoneNumber: str):
        if self._formattedDestinationExists(phoneNumber):
            compDestsList = self._getMappedDestinations(phoneNumber)
            pvl = PersonalisedValuesList()

            for compDest in compDestsList:
                pvl.add(compDest.getData())

            # return the personalised values list
            return pvl

        # nothing to return
        return None

    #
    # get personalised values for destination
    def getPersonalisedValues(self, phoneNumber: str) ->PersonalisedValuesList:
        if phoneNumber is None or len(phoneNumber) == 0:
            raise Exception("Invalid reference to phone number for personalised values.")

        # message should be set as personalised
        if not self.personalise():
            raise Exception("Message is not personalised for getting personalised values.")

        # destination should exist
        if not self.destinationExists(phoneNumber):
            raise Exception("Phone number '%s' does not exist for getting personalised values." % phoneNumber)

        return self.__getDestinationPersonalisedValues(self._getFormattedPhoneNumber(phoneNumber))

    # get personalised values for a specified messageId
    def getPersonalisedValuesById(self, messageId: str) ->list:
        if messageId is None or len(messageId) == 0:
            raise Exception("Invalid reference to message identifier for personalised values.")

        # ensure messageId exists
        if not self.messageIdExists(messageId):
            raise Exception("Message identifier '%s' does not exist." % messageId)

        # get the composer destination object and obtain the values
        pv = self._getMappedDestinationById(messageId).getData()

        if pv is not None:
            return pv.export()

        # no personalised values
        return None

    # validates personalised values before update
    def __validatePersonalisedValuesForUpdate(self, phoneNumber: str, newValues: list, prevValues: list = None):
        if phoneNumber is None or len(phoneNumber) == 0:
            raise Exception("Invalid phone number for updating personalised values.")

        # the message must be personalised
        if not self.personalise():
            raise Exception("Message is not set to be personalised.")

        # destination must exist
        if not self.destinationExists(phoneNumber):
            raise Exception("Phone number '%s' does not exist." % phoneNumber)

        # assert values
        self.__assertPersonalisedValues(phoneNumber, newValues, True)

        # if previous values are provided, we must ensure it is valid
        if prevValues is not None:
            self.__assertPersonalisedValues(phoneNumber, prevValues, True)

    # updates personalised values for a specified messageId
    def updatePersonalisedValuesById(self, messageId: str, newValues: list) ->bool:
        # the messageId must exist
        if messageId is None or len(messageId) == 0:
            raise Exception("Invalid reference to message identifier for updating personalised values.")

        # it must exist
        if not self.messageIdExists(messageId):
            raise Exception("Message identifier '%s' does not exist." % messageId)

        compDest: ComposerDestination = self._getComposerDestinationById(messageId)
        pv: PersonalisedValues = compDest.getData()

        if pv is None:
            raise Exception("The specified destination does not have personalised values for update.")

        # perform validation of the values
        self.__validatePersonalisedValuesForUpdate(compDest.getPhoneNumber(), newValues, pv.export())

        # perform the update
        return self.__updateComposerDestinationValues(compDest, newValues)

    # updates personalised values for specified phone number
    def updatePersonalisedValues(self, phoneNumber: str, newValues: list, prevValues: list = None):
        # validate
        self.__validatePersonalisedValuesForUpdate(phoneNumber, newValues, prevValues)
        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)

        # if no previous values are specified, then any existiing list of destinations
        # for the phone number will be replaced
        if prevValues is None:
            return self.__replacePersonalisedValues(fmtdNumber, newValues)
        else:
            # new personalised values should not already exist for the destination
            if self.__valuesExist(self.getPersonalisedValues(fmtdNumber, newValues)):
                raise Exception("The new personalised values already exist for destination '%s'." % phoneNumber)

            for compDest in self._getComposerDestinations(fmtdNumber):
                if not self.__valuesMatch(compDest.getData().export(), prevValues):
                    continue
                else:
                    return self.__updateComposerDestinationValues(compDest, newValues)

            # no update was performed
            return False

    # updates composer destination values
    def __updateComposerDestinationValues(self, compDest: ComposerDestination, values: list) ->bool:
        scheduled = compDest.isScheduled()
        messageId = compDest.getMessageId()
        phoneNumber = compDest.getPhoneNumber()
        destMode = DestinationMode.DM_UPDATE if scheduled == True else compDest.getWriteMode()

        # create new personalised values object
        pv = PersonalisedValues(values)
        newCompDest = self._createComposerDestination(phoneNumber, messageId, destMode, pv, scheduled)
        countryCode = self._getDestinationCountryCode(phoneNumber)

        # remove and replace with new
        if self._removeComposerDestination(compDest):
            self._addComposerDestination(newCompDest, countryCode)
            return True

        # no update performed
        return False

    def updatePersonalisedValuesWithId(self, phoneNumber: str, newValues: list, newMessageId: str) ->bool:
        if phoneNumber is None or not PhoneUtil.isValidPhoneNumber(phoneNumber):
            raise Exception("Invalid phone number for updating personalised values.")

        # validate message identifier
        if newMessageId is None or len(newMessageId) == 0:
            raise Exception("Invalid message identifier for updating personalised values.")

        # messageId should not already exist
        if self.messageIdExists(newMessageId):
            raise Exception("Message identifier '%s' already exists." % newMessageId)

        # format phone number
        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)

        # it should exist
        if not self._formattedDestinationExists(fmtdNumber):
            raise Exception("Phone number '%s' does not exist." % phoneNumber)

        # call for replacement
        return self.__replacePersonalisedValues(fmtdNumber, newValues, newMessageId)

    def __replacePersonalisedValues(self, phoneNumber: str, newValues, messageId: str = None) ->bool:
        # message should be set to be personalised
        if not self.personalise():
            raise Exception("Message is not personalised for updating values.")

        self.__validatePersonalisedValuesForUpdate(phoneNumber, newValues)

        fmtdNumber = self._getFormattedPhoneNumber(phoneNumber)
        countryCode = self._getDestinationCountryCode(fmtdNumber)
        compDestsList = self._getComposerDestinations(fmtdNumber)

        # remove associated composer destinations list
        self._removeComposerDestinationsList(fmtdNumber, compDestsList)

        # create new for replacement
        destMode = DestinationMode.DM_ADD
        pValues = PersonalisedValues(newValues)
        compDest = self._createComposerDestination(fmtdNumber, messageId, destMode, pValues)

        # add and return
        self._addComposerDestination(compDest, countryCode)
        return True

    # sets the message text
    def setMessage(self, message: str, personalise = None):
        if message is None or len(message) == 0:
            raise Exception("Invalid SMS message text.")

        if personalise is not None and not isinstance(personalise, bool):
            raise Exception("Invalid message personalisation flag.")

        # we should know if variables are defined. SMS being personalised should contain variables
        varsCount = SMSComposer.getMessageVariablesCount(message)

        if personalise is not None and personalise == True and varsCount == 0:
            raise Exception("Message text does not contain variables to personalise messages.")

        # set value for psnd (either True or False)
        if personalise is None:
            personalise = True if varsCount > 0 else False

        # see if the message text has been set, then do further validation
        messageText = self.getMessage()

        if messageText is not None and len(messageText) > 0:
            # If the message was initialised from a scheduled message, then we will want both to be
            # the same in terms of being personalised or not. And if personalised, they should have the same number of variables
            if self._isScheduled():
                self.__validateScheduledMessageTextUpdate(message, True if personalise is not None and personalise == True else False)

            # if the message was not previously personalised and is now being personalised,
            # then any existing destinations that were added will have to be cleared
            if (personalise == True and not self.personalise()) or (personalise is None or personalise == False and self.personalise()):
                self.clearDestinations()

        # set the message text
        self._message = message
        self.__personalise = personalise

    # validates the message text for scheduled message that has been loaded
    def __validateScheduledMessageTextUpdate(self, message: str, psn: bool):
        if psn == True and not self.personalise():    # loaded message is not personalised but current message is to be personalised
            raise Exception("Cannot replace non-personalised scheduled message with a personalised message.")

        # if the scheduled message was personalised and the new message
        # to be set is not personalised, we will not allow it
        if not psn == True and self.personalise():
            raise Exception("Cannot replace a personalised scheduled message with non-personalised message.")

        # if both are personalised, they should have the same number of variables defined in them
        if psn == True and self.personalise():
            schedMsgVarsCount = SMSComposer.getMessageVariablesCount(self._message)
            newMsgVarsCount = SMSComposer.getMessageVariablesCount(message)

            if schedMsgVarsCount != newMsgVarsCount:
                raise Exception("Mismatch variables count in scheduled message text and replacement message text.")

    # gets the text message type
    def getSMSType(self) ->SMSType:
        return self.__type

    # sets the message type
    def setSMSType(self, type: SMSType):
        if type is None or isinstance(type, SMSType) == False:
            raise Exception("Invalid text message type specifier.")

        self.__type = type

    # sets message sender Id
    def setSender(self, sender: str):
        if sender is None or len(sender) == 0:
            raise Exception("Missing or invalid message sender identifier.")

        if PhoneUtil.isValidPhoneNumber(sender):
            if len(sender) > SMSComposer.__NUMERIC_SENDER_MAX_LEN__:
                raise Exception("Numeric sender identifier must not be greater than %d characters." % SMSComposer.__NUMERIC_SENDER_MAX_LEN__)
        else:
            if len(sender) > SMSComposer.__ALPHA_NUMERIC_SENDER_MAX_LEN__:
                raise Exception("Alpha-numeric sender identifier must not be greater than %d characters." % SMSComposer.__ALPHA_NUMERIC_SENDER_MAX_LEN__)

        # parent should set it
        super().setSender(sender)
