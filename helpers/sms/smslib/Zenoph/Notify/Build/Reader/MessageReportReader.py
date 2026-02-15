from email.message import Message
from xml.dom import pulldom
from xml.etree import ElementTree

from Zenoph.Notify.Utils.XMLUtil import XMLUtil
from Zenoph.Notify.Enums.SMSType import SMSType
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Report.MessageReport import MessageReport
from Zenoph.Notify.Collections.MessageDestinationsList import MessageDestinationsList
from Zenoph.Notify.Build.Reader.MessageDestinationsReader import MessageDestinationsReader
from Zenoph.Notify.Utils.MessageReportUtil import MessageReportUtil
from Zenoph.Notify.Utils.MessageUtil import MessageUtil

class MessageReportReader(object):
    def __init__(self):
        self.__done = False
        self.__xmlDoc = None

    def setData(self, data: object):
        if data is None or isinstance(data, str) == False or len(data) == 0:
            raise Exception("Invalid data for reading message reports.")

        # initialise the XML document
        self.__xmlDoc = XMLUtil.createXMLDocument(data)


    def read(self) ->MessageReport:
        if self.__xmlDoc is None:
            raise Exception("Invalid object reference to data for creating message report item.")

        # read the document and extract relevant data
        for event, node in self.__xmlDoc:
            if event == pulldom.START_ELEMENT and node.localName == "data":
                return self.__readMessageReport(self.__xmlDoc)
            elif event == pulldom.END_ELEMENT and node.localName == "data":
                break

        # nothing to return at this point
        return None


    def __readMessageReport(self, xmlDoc: pulldom.DOMEventStream) ->MessageReport:
        done = False
        report = MessageReport()
        data: dict = {}

        while not done:
            eventInfo = xmlDoc.getEvent()

            if eventInfo is not None:
                event = eventInfo[0]
                node = eventInfo[1]

                if event == pulldom.START_ELEMENT:
                    nodeName = node.localName

                    if nodeName == "batch":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["batch"] = tree.text

                    elif nodeName == 'category':
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data['category'] = MessageUtil.messageCategoryToEnum(tree.text)  # MessageCategory(int(tree.text))

                    # message text
                    elif nodeName == "text":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["text"] = tree.text

                    # message type
                    elif nodeName == "type":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["type"] = SMSType(int(tree.text))

                    # message sender id
                    elif nodeName == "sender":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["sender"] = tree.text

                    # whether message is was personalised or not (SMS)
                    elif nodeName == "personalised":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["personalised"] = tree.text == "true"

                    # whether report is for message delivery request or not
                    elif nodeName == "delivery":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["delivery"] = tree.text == "true"

                    # destinations count
                    elif nodeName == "destinationsCount":
                        xmlDoc.expandNode(node)
                        tree = ElementTree.fromstring(node.toxml())
                        data["destsCount"] = int(tree.text)

                    # message destinations
                    elif nodeName == "destinations":
                        data["destinations"] = self.__readMessageDestinations(xmlDoc)

                elif event == pulldom.END_ELEMENT and node.localName == "data":
                    done = True
                        
            else:
                done = True

        # if we have report data, set it
        if data is not None and len(data) > 0:
            report = MessageReportUtil.createReport(data)

        # return the message report object
        return report

    #
    # reads destinations in from a message response
    def __readMessageDestinations(self, xmlDoc: pulldom.DOMEventStream) ->MessageDestinationsList:
        done = False
        destsList = MessageDestinationsList()
        destsReader = MessageDestinationsReader()
        destsReader.setData(xmlDoc)

        while True:
            msgDest = destsReader.getNextItem()

            if msgDest is None:
                break

            destsList.add(msgDest)

        # return destinations data
        return destsList if destsList.getCount() > 0 else None