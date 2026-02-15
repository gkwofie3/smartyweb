from xml.dom import pulldom
from xml.etree import ElementTree

from Zenoph.Notify.Store.MessageDestination import MessageDestination
from Zenoph.Notify.Store.PersonalisedValues import PersonalisedValues
from Zenoph.Notify.Enums.DestinationValidation import DestinationValidation

class MessageDestinationsReader:
    def __init__(self):
        self.__done = False
        self.__xmlDoc: pulldom.DOMEventStream = None

    def setData(self, data: pulldom.DOMEventStream):
        if data is None or not isinstance(data, pulldom.DOMEventStream):
            raise Exception("Invalid object reference for reading message destinations.")

        # set the data
        self.__xmlDoc = data

    def getNextItem(self) ->MessageDestination:
        # xml document data should already be set
        if self.__xmlDoc is None:
            raise Exception("Destinations data has not been set for reading message destinations.")

        done = False

        while not done:
            eventInfo = self.__xmlDoc.getEvent()
            node = eventInfo[1]

            if eventInfo[0] == pulldom.START_ELEMENT and node.localName == "item":
                self.__xmlDoc.expandNode(node)
                return self.__readDestinationItem(node.toxml())

            # check for END_ELEMENT. if we have destinations, then we are done reading the destinations
            elif eventInfo[0] == pulldom.END_ELEMENT and eventInfo[1].localName == "destinations":
                done = True

        # at this point we return nothing
        return None

    def __readDestinationItem(self, itemXml: str) ->MessageDestination:
        tree = ElementTree.fromstring(itemXml)
        data: dict = {}

        # phone number
        node = tree.find("to")
        if node is not None:
            data["phoneNumber"] = node.text

        # country name
        node = tree.find("country")
        if node is not None:
            data["country"] = node.text

        # destination message Id
        node = tree.find("id")
        if node is not None:
            data["messageId"] = node.text

        # message text
        node = tree.find("message")
        if node is not None:
            data["message"] = node.text

        # status
        node = tree.find("status")
        if node is not None:
            data["statusId"] = int(node.find("id").text)

        # validation
        node = tree.find("validation")
        if node is not None:
            data["destValidation"] = DestinationValidation(int(node.find("id").text))

        # message count
        node = tree.find("messageCount")
        if node is not None:
            data["messageCount"] = int(node.text)

        # message submit date and time
        node = tree.find("submitDateTime")
        if node is not None:
            data["submitDateTime"] = node.text

        # report date and time
        node = tree.find("reportDateTime")
        if node is not None:
            data["reportDateTime"] = node.text

        # personalised values
        nodeList = tree.findall("values/value")
        if nodeList is not None and len(nodeList) > 0:
            values = []

            for node in nodeList:
                values.append(node.text)

            # set the personalised values
            data["psndValues"] = PersonalisedValues(values)


        # if we captured any value in the data, then we should create the destination object
        if len(data) > 0:
            return MessageDestination.create(data)
        else:
            return None
