#from Zenoph.Notify.Enums import TextMessageType
#from Zenoph.Notify.Compose import ISMSComposer, SMSComposer
#from Zenoph.Notify.Request import MessageRequest

from Zenoph.Notify.Enums.SMSType import SMSType
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Compose.ISMSComposer import ISMSComposer
from Zenoph.Notify.Compose.SMSComposer import SMSComposer
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Request.MessageRequest import MessageRequest
from Zenoph.Notify.Response.MessageResponse import MessageResponse

class SMSRequest(MessageRequest, ISMSComposer):
    __BASE_RESOURCE__ = "message/sms/send"

    def __init__(self, ap: AuthProfile = None):
        super().__init__(ap)

        if ap is None:
            self._composer = SMSComposer()
        else:
            self._composer = SMSComposer(ap)   

    # validates data
    def _validate(self):

        # message sender Id is mandatory for SMS
        sender = self._composer.getSender()
        msgType = self._composer.getSMSType()
        
        if sender is None or sender == "":
            raise Exception("Message sender has not been set.")
    
    @staticmethod
    def getBaseResource():
        return SMSRequest.__BASE_RESOURCE__

    @staticmethod
    def submitComposer(sc: SMSComposer, param1, param2 = None):
        if sc is None or not isinstance(sc, SMSComposer):
            raise Exception("Invalid SMS composer object for dispatching message.")

        # parameter must be provided. It is either a string (API key) or AuthProfile object
        if param1 is None or isinstance(param1, AuthProfile) == False or isinstance(param1, str) == False:
            raise Exception("Invalid authentication parameter for dispatching message.")

        sr = SMSRequest()
        sr._composer = sc
        SMSRequest._initRequestAuth(sr, param1, param2)

        # submit and return response
        return sr.submit()

    @staticmethod
    def getMessageCount(message: str, type: SMSType) ->int:
        return SMSComposer.getMessageCount(message, type)

    @staticmethod
    def getMessageVariablesCount(message) ->int:
        return SMSComposer.getMessageVariablesCount(message)

    @staticmethod
    def getMessageVariables(message: str, trim: bool = False):
        return SMSComposer.getMessageVariables(message, trim)

    # submits sms
    def submit(self):
        self._validate()
        self._setRequestResource(SMSRequest.__BASE_RESOURCE__)

        self._initHttpRequest()
        writer = self._createDataWriter()
        self._requestData = writer.getSMSRequestData(self._composer)

        # submit for response
        response = super().submit()

        # create and return the message response object
        return MessageResponse.create(response)

    # gets sender Ids
    def getRegisteredSenderIds(self):
        self._assertComposer()
        return self._composer.getRegisteredSenderIds()

    # sets message type
    def setSMSType(self, type: SMSType):
        self._assertComposer()
        self._composer.setSMSType(type)

    # gets message type
    def getSMSType(self) ->SMSType:
        self._assertComposer()
        return self._composer.getSMSType()

    # indicates whether message will be personalised or not
    def personalise(self) ->bool:
        self._assertComposer()
        return self._composer.personalise()

    # gets default text message type
    def getDefaultSMSType(self) ->SMSType:
        self._assertComposer()
        return self._composer.getDefaultSMSType()

    # gets personalised values
    def getPersonalisedValues(self, phoneNumber: str):
        self._assertComposer()
        return self._composer.getPersonalisedValues(phoneNumber)

    # get personalised values for specified phone number
    def getPersonalisedValuesById(self, messageId: str):
        self._assertComposer()
        return self._composer.getPersonalisedValuesById(messageId)

    # updates personalised values for specified messageId
    def updatePersonalisedValuesById(self, messageId: str, values) ->bool:
        self._assertComposer()
        return self._composer.updatePersonalisedValuesById(messageId, values)

    # updates personalised values for specified phone number
    def updatePersonalisedValues(self, phoneNumber: str, newValues, prevValues = None) ->bool:
        self._assertComposer()
        return self._composer.updatePersonalisedValues(phoneNumber, newValues, prevValues)

    # updates personalised values with Id
    def updatePersonalisedValuesWithId(self, phoneNumber: str, newValues, newMessageId: str) ->bool:
        self._assertComposer()
        return self._composer.updatePersonalisedValuesWithId(phoneNumber, newValues, newMessageId)

    # remove personalised values for specified phone number
    def removePersonalisedValues(self, phoneNumber: str, values) ->bool:
        self._assertComposer()
        return self._composer.removePersonalisedValues(phoneNumber, values)

    # removes personalised destination
    def removePersonalisedDestination(self, phoneNumber: str, values) ->bool:
        self._assertComposer()
        return self._composer.removePersonalisedDestination(phoneNumber, values)

    # adds personalised destination
    def addPersonalisedDestination(self, phoneNumber: str, throwEx: bool, values, messageId: str = None):
        self._assertComposer()
        return self._composer.addPersonalisedDestination(phoneNumber, throwEx, values, messageId)

    # gets messageId associated with a personalised destination
    def getPersonalisedDestinationMessageId(self, phoneNumber: str, values) ->str:
        self._assertComposer()
        return self._composer.getPersonalisedDestinationMessageId(phoneNumber, values)

    # gets the write mode for personalised destination
    def getPersonalisedDestinationWriteMode(self, phoneNumber: str, values) ->DestinationMode:
        self._assertComposer()
        return self._composer.getPersonalisedDestinationWriteMode(phoneNumber, values)

    # checks to see if personalised values exist for specified phone number
    def personalisedValuesExists(self, phoneNumber: str, values) ->bool:
        self._assertComposer()
        return self._composer.personalisedValuesExists(phoneNumber, values)

