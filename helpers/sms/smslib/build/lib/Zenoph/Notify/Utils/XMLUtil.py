from abc import ABC
from xml.dom import pulldom

class XMLUtil(ABC):
    def __init__(self):
        pass

    @staticmethod
    def createXMLDocument(xmlStr: str):
        return pulldom.parseString(xmlStr)
