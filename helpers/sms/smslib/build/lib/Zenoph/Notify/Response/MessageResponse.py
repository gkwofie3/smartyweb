from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Report.MessageReport import MessageReport
from Zenoph.Notify.Response.APIResponse import APIResponse
from Zenoph.Notify.Build.Reader.MessageReportReader import MessageReportReader

class MessageResponse(APIResponse):
    __RESPONSE_FRAGMENT_PATTERN__ = "<data>(.*)?<\/data>"

    def __init__(self):
        self.__report: MessageReport = None

    @staticmethod
    def create(apiResp: APIResponse):
        msgResp = MessageResponse()
        msgResp._httpStatusCode = apiResp.getHttpStatusCode()
        msgResp._handshake = apiResp.getRequestHandshake()

        dataFragment = apiResp.getDataFragment()

        if dataFragment is not None and len(dataFragment) > 0:
            if not MessageResponse.isValidDataFragment(dataFragment):
                raise Exception("Invalid response data fragment.")

            msgResp.__report = MessageResponse.extractReport(dataFragment)

        # return message response
        return msgResp

    @staticmethod
    def extractReport(dataFragment: str) ->MessageReport:
        reportReader = MessageReportReader()
        reportReader.setData(dataFragment)
         
        # read and return message report
        return reportReader.read();

    @staticmethod
    def isValidDataFragment(dataFragment: str):
        return MessageUtil.isRegexMatch("%s%s%s" % ("^", MessageResponse.__RESPONSE_FRAGMENT_PATTERN__, "$"), dataFragment, True)

    def getReport(self):
        return self.__report