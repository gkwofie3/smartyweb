from Zenoph.Notify.Compose.MessageComposer import MessageComposer
from Zenoph.Notify.Collections.IDataList import IDataList

class MessageComposerList(IDataList):
    def __init__(self):
        self.__messagesList = []

    def add(self, item: MessageComposer):
        if item is None or not isinstance(item, MessageComposer):
            raise Exception("Invalid object reference for adding to message composer list.")

        self.__messagesList.append(item)

    def get(self, idx) ->MessageComposer:
        if idx < 0 or idx > len(self.__messagesList) - 1:
            raise Exception("Index out of range for getting message composer item.")

        return self.__messagesList[idx]

    def getCount(self) ->int:
        return len(self.__messagesList)

    def __iter__(self):
        for mc in self.__messagesList:
            yield mc
