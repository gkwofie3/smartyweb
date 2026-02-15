import abc

class IComposer(abc.ABC):
    @abc.abstractmethod
    def addDestination(self, phoneNumber: str, throwEx: bool = False, messageId: str = None):
        pass

    @abc.abstractmethod
    def addDestinationsFromTextStream(self, stream: str):
        pass

    @abc.abstractmethod
    def addDestinationsFromCollection(self, coll: list, throwEx = False):
        pass

    @abc.abstractmethod
    def getDestinationCountry(self, phoneNumber: str) ->str :
        pass

    @abc.abstractmethod
    def getDefaultDestinationCountry(self):
        pass

    @abc.abstractmethod
    def getDestinations(self):
        pass

    @abc.abstractmethod
    def getDestinationsCount(self) ->int:
        pass

    @abc.abstractmethod
    def getDestinationWriteMode(self, phoneNumber: str):
        pass

    @abc.abstractmethod
    def getDestinationWriteModeById(self, messageId: str):
        pass

    @abc.abstractmethod
    def destinationExists(self, phoneNumber: str):
        pass

    @abc.abstractmethod
    def clearDestinations(self):
        pass

    @abc.abstractmethod
    def removeDestination(self, phoneNumber: str):
        pass

    @abc.abstractmethod
    def removeDestinationById(self, messageId: str):
        pass

    @abc.abstractmethod
    def updateDestination(self, prePhoneNumber: str, newPhoneNumber: str):
        pass

    @abc.abstractmethod
    def updateDestinationById(self, messageId: str, newPhoneNumber: str):
        pass

    @abc.abstractmethod
    def getCategory(self):
        pass

    @abc.abstractmethod
    def getDefaultTimeZone(self):
        pass

    @abc.abstractmethod
    def getRouteCountries(self):
        pass

    @abc.abstractmethod
    def setDefaultNumberPrefix(self, prefix: str):
        pass

    @abc.abstractmethod
    def getDefaultNumberPrefix(self):
        pass
