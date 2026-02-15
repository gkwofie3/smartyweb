from xml.etree import ElementTree
from xml.dom import pulldom

from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Utils.XMLUtil import XMLUtil
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Utils.RequestUtil import RequestUtil
from Zenoph.Notify.Compose.SMSComposer import SMSComposer
from Zenoph.Notify.Compose.VoiceComposer import VoiceComposer
from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Collections.MessageComposerList import MessageComposerList
from Zenoph.Notify.Enums.SMSType import SMSType

class MessagePropertiesReader:
    def __init__(self):
        self.__authProfile: AuthProfile = None
        self.__fragment: str = None
        self.__isScheduled: bool = False
        self.__done: bool = False
        self.__xmlDoc = None

    def setAuthProfile(self, ap: AuthProfile):
        if ap is not None:
            if not isinstance(ap, AuthProfile):
                raise Exception("Invalid reference to Authentication profile object for reading message properties.")

            self.__authProfile = ap

    def setDataFragment(self, data: str):
        if data is None or not isinstance(data, str) or len(data) == 0:
            raise Exception("Invalid data for reading message properties.")

        self.__xmlDoc = XMLUtil.createXMLDocument(data)

    def isScheduled(self, scheduled: bool):
        if not isinstance(scheduled, bool):
            raise Exception("Invalid specifier for message scheduling state.")

        self.__isScheduled = scheduled

    def __setTextMessageProperties(self, mc: MessageComposer, tree):
        mc.setMessageType(SMSType(int(tree.find("type").text)))

        personalised = True if tree.find("personalise").text == "true" else False
        messageText = tree.find("text").text

        mc.setMessage(messageText, personalised)
        mc.setSender(tree.find("sender").text)


    def __setVoiceMessageProperties(self, mc: MessageComposer, tree):
        pass

    def __readMessage(self, xmlStr):
        mc: MessageComposer = None
        tree = ElementTree.fromstring(xmlStr)

        batchId = tree.find('batch').text
        category = MessageUtil.messageCategoryToEnum(tree.find('category').text) # MessageCategory(int(tree.find('category').text))

        data = {'batch': batchId, 'category': category, 'scheduled': self.__isScheduled}

        if self.__authProfile is not None:
            data['authProfile'] = self.__authProfile

        if category == MessageCategory.SMS:
            mc = SMSComposer.create(data)
            self.__setTextMessageProperties(mc, tree)
        elif category == MessageCategory.VOICE:
            mc = VoiceComposer.create(data)
            self.__setVoiceMessageProperties(mc, tree)

        # set common message properties
        self.__setCommonMessageProperties(mc, tree)

        # return message composer
        return mc

    def __setCommonMessageProperties(self, mc: MessageComposer, tree):
        if (isinstance(mc, MessageComposer)):
            node = tree.find('schedule/dateTime')

            if node is not None:
                dateTime = node.text
                offset = tree.find('schedule/offset').text

                # set the schedule datetime and utc offset
                mc.setScheduleDateTime(dateTime, offset);

            # check delivery report notification URL
            node = tree.find('callback/url')

            if node is not None:
                url = node.text
                accept = RequestUtil.getDataContentTypeFromLabel(tree.find('callback/accept').text)

                # set delivery callback url
                mc.setDeliveryCallback(url, accept)

            # check for message sender name
            node = tree.find('sender')

            if node is not None:
                mc.setSender(node.text)


    def __getNextMessage(self):
        done = False

        while not done:
            eventInfo = self.__xmlDoc.getEvent()
            node = eventInfo[1]

            if eventInfo[0] == pulldom.START_ELEMENT and node.localName == "message":
                self.__xmlDoc.expandNode(node)
                return self.__readMessage(node.toxml())
            elif eventInfo[0] == pulldom.END_ELEMENT and node.localName == "data":
                done = True

        # return nothing at this point
        return None

    def getMessages(self):
        msgsList: MessageComposerList = MessageComposerList()

        while True:
            composer = self.__getNextMessage()

            if composer is None:
                break 

            # add to the collection
            msgsList.add(composer)

        # return messages list
        return msgsList
