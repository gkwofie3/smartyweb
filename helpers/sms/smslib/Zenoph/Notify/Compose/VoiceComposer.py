import os

from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Compose.IVoiceComposer import IVoiceComposer
from Zenoph.Notify.Compose.ISchedule import ISchedule

class VoiceComposer(MessageComposer, IVoiceComposer, ISchedule):
    def __init__(self, ap: AuthProfile):
        # base constructor call
        super().__init__(ap)
        
        self.__offlineVoiceFile: str = None
        self.__templateVoiceRef: str = None

        # message category
        self._category = MessageCategory.VOICE

    @staticmethod
    def create(data: object):
        pass

    def setTemplateReference(self, reference: str):
        if reference is None or not isinstance(reference, str) or len(reference) == 0:
            raise Exception("Invalid voice reference name.")

        # we will not upload file since a saved voice reference is being set
        self.__offlineVoiceFile = None

        # set the reference to saved voice
        self.__templateVoiceRef = reference

    def getTemplateReference(self) ->str:
        return self.__templateVoiceRef

    def setOfflineVoice(self, fileName: str, reference: str = None):
        if fileName is None or len(fileName) == 0:
            raise Exception("Invalid offline voice file name.")

        if reference is not None and len(reference) == 0:
            raise Exception("Invalid reference name for saving voice file.")

        if not os.path.isfile(fileName):
            raise Exception("Voice file '%s' does not exist." % fileName)

        # set the offline file
        self.__offlineVoiceFile = fileName
        self.__templateVoiceRef = reference if reference is not None else None
