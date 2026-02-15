import abc

class ISMSComposer(abc.ABC):
    @abc.abstractmethod
    def setSMSType(self, type):
        pass

    @abc.abstractmethod
    def getSMSType(self):
        pass

    @abc.abstractmethod
    def personalise(self):
        pass

    @abc.abstractmethod
    def getPersonalisedDestinationMessageId(self, phoneNumber, values):
        pass

    @abc.abstractmethod
    def getPersonalisedDestinationWriteMode(self, phoneNumber, values):
        pass

    @abc.abstractmethod
    def addPersonalisedDestination(self, phoneNumber, throwEx, values, messageId = None):
        pass

    @abc.abstractmethod
    def personalisedValuesExists(self, phoneNumber, values):
        pass

    @abc.abstractmethod
    def removePersonalisedValues(self, phoneNumber, values):
        pass

    @abc.abstractmethod
    def removePersonalisedDestination(self, phoneNumber, values):
        pass

    @abc.abstractmethod
    def updatePersonalisedValues(self, phoneNumber, newValues, prevValues = None):
        pass

    @abc.abstractmethod
    def updatePersonalisedValuesById(self, messageId, newValues):
        pass

    @abc.abstractmethod
    def updatePersonalisedValuesWithId(self, phoneNumber, newValues, newMessageId):
        pass

    @abc.abstractmethod
    def getPersonalisedValues(self, phoneNumber):
        pass

    @abc.abstractmethod
    def getPersonalisedValuesById(self, messageId):
        pass

    @abc.abstractmethod
    def getDefaultSMSType(self):
        pass

    @abc.abstractmethod
    def getRegisteredSenderIds(self):
        pass
