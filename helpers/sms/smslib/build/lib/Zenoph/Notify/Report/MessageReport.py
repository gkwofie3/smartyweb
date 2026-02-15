
from abc import ABC

from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Collections.MessageDestinationsList import MessageDestinationsList

class MessageReport(ABC):
    def __init__(self):
        self.__batchId: str = None
        self.__category: MessageCategory = None
        self.__deliveryReport: bool = False
        self.__destsList: MessageDestinationsList = MessageDestinationsList()

    #
    # creates a message report object
    def _setCommonProperties(self, p: dict):
        # message reference
        if "batch" in p:
            self.__batchId = p["batch"]

        # message category
        if "category" in p:
            self.__category = p["category"]

        # whether delivery report or not
        if "delivery" in p:
            self.__deliveryReport = p["delivery"]

        # message destinations
        if "destinations" in p:
            self.__destsList = p["destinations"]

    #
    # gets the reference assigned to the message
    def getBatchId(self) ->str:
        return self.__batchId

    #
    # gets the message category
    def getCategory(self) ->MessageCategory:
        return self.__category

    #
    # gets indicator to know if we have delivery report
    def isDeliveryReport(self):
        return self.__deliveryReport

    #
    # gets the message destinations count
    def getDestinationCount(self) ->int:
        return len(self.__destsList)

    #
    # gets the list of message destinations
    def getDestinations(self) ->MessageDestinationsList:
        return self.__destsList
