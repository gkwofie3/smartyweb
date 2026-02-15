
from Zenoph.Notify.Report.MessageReport import MessageReport

class SMSReport(MessageReport):
    def __init__(self):
    #    super().__init__()

        self.__sender: str = None
        self.__text: str = None
        self.__type: object = None
        self.__personalised: bool = False


    @staticmethod 
    def create(p: dict):
        if p is None or isinstance(p, dict) == False:
            raise Exception("Invalid object reference for creating message report object.")

        # instantiate message report object
        report = SMSReport()

        # call to set common properties
        report._setCommonProperties(p);

        # sender Id
        if "sender" in p:
            report.__sender = p["sender"]

        # message text
        if "text" in p:
            report.__text = p["text"]

        # message type
        if "type" in p:
            report.__type = p["type"]

        # personalised SMS or not
        if "personalised" in p:
            report.__personalised = p["personalised"]

        # return the message report object
        return report

    #
    # gets the message
    def getMessage(self) ->str:
        return self.__text

    #
    # gets the message sender Id
    def getSender(self) ->str:
        return self.__sender

    #
    # gets the message type [for SMS]
    def getSMSType(self):
        return self.__type

    #
    # indicates whether message was personalised or not
    def isPersonalised(self) ->bool:
        return self.__personalised