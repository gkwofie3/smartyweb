import abc
import re
from datetime import datetime
from xml.dom import pulldom
from xml.etree import ElementTree

from Zenoph.Notify.Enums.SMSType import SMSType
from Zenoph.Notify.Enums.MessageCategory import MessageCategory

class MessageUtil(abc.ABC):
    CUSTOM_MSGID_MIN_LEN = 30
    CUSTOM_MSGID_MAX_LEN = 40
    TZ_OFFSET_PATTERN = "^(\+|-)(([0][0-9]:[0-5][0-9])|([1][0-2]:[0-5][0-9])|(13:00))$";

    __timeZones: dict = None
    __messageTypes: list = None

    @staticmethod
    def isRegexMatch(pattern: str, value: str, dotAllMode: bool = False) ->bool:
        match = re.match(pattern, value, re.DOTALL) if dotAllMode else re.match(pattern, value)
       
        # if it matched, then it will not be None
        return not match is None

    @staticmethod
    def isValidTimeZoneOffset(offset: str) ->bool:
        return MessageUtil.isRegexMatch(MessageUtil.TZ_OFFSET_PATTERN, offset)

    @staticmethod
    def isNumericSender(senderId: str) ->bool:
        return MessageUtil.isRegexMatch("^(\+)?\d+$", senderId)

    @staticmethod
    def extractGeneralSettings(tree: ElementTree.Element):
        MessageUtil.__timeZones = MessageUtil.__extractTimeZones(tree)
        MessageUtil.__messageTypes = MessageUtil.__extractMessageTypes(tree)

    @staticmethod
    def __extractMessageTypes(tree: ElementTree.Element) ->list:
        typesList = []

        for node in tree.findall("settings/general/messageTypes/type"):
            n = node.find("id")

            type = {}
            type["id"] = int(node.find("id").text)
            type["label"] = node.find("label").text
            type["singleLen"] = int(node.find("singleLen").text)
            type["concatLen"] = int(node.find("concatLen").text)
            type["charLen"] = int(node.find("charLen").text)

            # add to the list
            typesList.append(type)

        # return types list
        return typesList

    @staticmethod
    def __extractTimeZones(tree: ElementTree.Element) ->dict:
        zones = {}

        for node in tree.findall("settings/general/timeZones/region"):
            regionName = node.attrib["name"]
            cities = []

            # each region has list of cities and their corresponding UTC offsets
            for cityNode in node.findall("city"):
                cities.append([cityNode.text, cityNode.attrib["offset"]])

            zones[regionName] = cities

        # return time zones
        return zones


    @staticmethod 
    def messageCategoryToEnum(category: str) ->MessageCategory:
        if category == 'sms':
            return MessageCategory.SMS
        elif category == 'voice':
            return MessageCategory.VOICE
        elif category == 'ussd':
            return MessageCategory.USSD
        else:
            raise Exception("Invalid message category specifier")


    #
    #
    @staticmethod
    def messageTypeToStr(type: SMSType) ->str:
        if type is None:
            raise Exception("Invalid message type specifier.")

        if MessageUtil.__messageTypes is None:
            raise Exception("Text message types have not been loaded.")

        for typeInfo in MessageUtil.__messageTypes:
            if int(typeInfo["id"]) == int(type):
                return typeInfo["label"]

        # not found
        raise Exception("Message type specifier was not found.")

    @staticmethod
    def messageTypeToEnum(type: str) ->SMSType:
        if type is None or len(type) == 0:
            raise Exception("Invalid reference to message type label.")

        if MessageUtil.__messageTypes is None:
            raise Exception("Text message types have not been loaded.")

        for typeInfo in MessageUtil.__messageTypes:
            if typeInfo["label"].lower() == type.lower():
                return SMSType(int(typeInfo["id"]))

        # not found
        raise Exception("Message type label '%s' was not found." % type)

    @staticmethod
    def getMessageTypeInfo(type: SMSType) ->dict:
        if MessageUtil.__messageTypes is None:
            return None

        for typeInfo in MessageUtil.__messageTypes:
            if int(type) == int(typeInfo["id"]):
                return typeInfo

        # not found
        raise Exception("Text message type identifier was not found.")

    @staticmethod
    def getTimeZones() ->dict:
        return MessageUtil.__timeZones

    @staticmethod
    def getMessageTypes() ->list:
        return MessageUtil.__messageTypes

    @staticmethod
    def getMessageCategoryLabel(category: MessageCategory) ->str:
        if category == MessageCategory.SMS:
            return "sms"
        elif category == MessageCategory.VOICE:
            return "voice"
        elif category == MessageCategory.USSD:
            return "ussd"
        else:
            raise Exception("Unknown message category identifier.")
