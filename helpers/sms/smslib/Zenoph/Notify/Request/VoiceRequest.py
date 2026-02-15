from Zenoph.Notify.Request.MessageRequest import MessageRequest
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Compose.IVoiceComposer import IVoiceComposer
from Zenoph.Notify.Compose.VoiceComposer import VoiceComposer
from Zenoph.Notify.Response.MessageResponse import MessageResponse
from Zenoph.Notify.Build.Writer.MultiPartDataWriter import MultiPartDataWriter
from Zenoph.Notify.Build.Writer.XmlDataWriter import XmlDataWriter
from Zenoph.Notify.Store.AuthProfile import AuthProfile

class VoiceRequest(MessageRequest, IVoiceComposer):
    __BASE_RESOURCE__ = "message/voice/send"
    __VOICE_UPLOAD_KEY_NAME__ = "voice_file"

    def __init__(self, ap: AuthProfile):
        super().__init__(ap)

        # initialise the message composer
        self._composer = VoiceComposer(ap)

    def setOfflineVoice(self, fileName: str, reference: str = None):
        self._assertComposer()
        self._composer.setOfflineVoice(fileName, reference)

    def getOfflineVoice(self):
        self._assertComposer()
        return self._composer.getOfflineVoice()

    def getTemplateReference(self):
        self._assertComposer()
        return self._composer.getTemplateReference()

    def isOfflineVoice(self):
        self._assertComposer()
        return self._composer.isOfflineVoice()

    def submit(self):
        pass