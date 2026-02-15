from Zenoph.Notify.Build.Writer.KeyValueDataWriter import KeyValueDataWriter
from Zenoph.Notify.Compose.VoiceComposer import VoiceComposer

class UrlEncodedDataWriter(KeyValueDataWriter):
    def __init__(self):
        super().__init__()

    def getVoiceRequestData(self, vc: VoiceComposer) ->dict:
        # there should be only one item
        # write the voice data
        self._writeVoiceMessageData(vc, self._keyValueStore)

        # prepare and return request data string
        return self._prepareRequestData()
