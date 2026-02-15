import abc

from Zenoph.Notify.Report.SMSReport import SMSReport
from Zenoph.Notify.Report.VoiceReport import VoiceReport
from Zenoph.Notify.Enums.MessageCategory import MessageCategory

class MessageReportUtil(abc.ABC):
    @staticmethod 
    def createReport(data: dict):
        if not 'category' in data:
            raise Exception('Missing message category specifier for report.')

        if data['category'] == MessageCategory.SMS:
            return SMSReport.create(data)
        elif data['category'] == MessageCategory.VOICE:
            return VoiceReport.create(data)
        else:
            raise Exception('Invalid message category specifier for report.');
