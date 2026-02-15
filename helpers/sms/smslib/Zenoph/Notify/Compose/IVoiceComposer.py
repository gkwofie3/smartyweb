import abc

class IVoiceComposer(abc.ABC):
    @abc.abstractmethod
    def setOfflineVoice(self, fileName, saveRef: str = None):
        pass

    @abc.abstractmethod
    def getOfflineVoice(self):
        pass

    @abc.abstractmethod
    def setTemplateReference(self, ref: str):
        pass

    @abc.abstractmethod
    def getTemplateReference(self):
        pass

    @abc.abstractmethod
    def isOfflineVoice(self):
        pass
