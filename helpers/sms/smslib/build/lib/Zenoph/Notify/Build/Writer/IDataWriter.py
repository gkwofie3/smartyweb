import abc
from http import client
from Zenoph.Notify.Compose.Composer import Composer
from Zenoph.Notify.Compose.SMSComposer import SMSComposer
from Zenoph.Notify.Compose.VoiceComposer import VoiceComposer

class IDataWriter(abc.ABC):
    @abc.abstractmethod
    def getScheduledMessageUpdateRequestData(self, mc: Composer):
        pass

    @abc.abstractmethod
    def getScheduledMessagesLoadRequestData(self, data: dict):
        pass

    @abc.abstractmethod
    def getDestinationsData(self, mc: Composer):
        pass

    @abc.abstractmethod
    def getSMSRequestData(self, sc: SMSComposer):
        pass

    @abc.abstractmethod
    def getVoiceRequestData(self, vc: VoiceComposer):
        pass

    @abc.abstractmethod
    def getUSSDRequestData(self, uc):
        pass

    @abc.abstractmethod
    def getDestinationsDeliveryRequestData(self, messageIds: list):
        pass