from Zenoph.Notify.Report.MessageReport import MessageReport

class VoiceReport(MessageReport):
    def __init__(self):
        super().__init__()

    @staticmethod 
    def create(data: dict):
        # initialise voice report object
        report = VoiceReport()

        # call base to set properties
        report._setCommonProperties(data);

        # return voice report
        return report

