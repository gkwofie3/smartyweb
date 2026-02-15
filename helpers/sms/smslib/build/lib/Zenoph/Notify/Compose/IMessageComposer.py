import abc

class IMessageComposer(abc.ABC):
    @abc.abstractmethod
    def setSender(self, sender: str):
        pass

    @abc.abstractmethod
    def getSender(self):
        pass

    @abc.abstractmethod
    def validateDestinationSenderName(self, phoneNumber: str):
        pass

    @abc.abstractmethod
    def setDeliveryCallback(self, url: str, type):
        pass

    @abc.abstractmethod
    def getDeliveryCallback(self):
        pass

    @abc.abstractmethod
    def notifyDeliveries(self):
        pass

    @abc.abstractmethod
    def setMessage(self, message: str, info = None):
        pass

    @abc.abstractmethod
    def getMessage(self):
        pass

    @abc.abstractmethod
    def getMessageId(self, phoneNumber: str):
        pass

    @abc.abstractclassmethod
    def messageIdExists(self, messageId: str):
        pass


