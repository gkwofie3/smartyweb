from Zenoph.Notify.Store.MessageDestination import MessageDestination
from Zenoph.Notify.Collections.IDataList import IDataList

class MessageDestinationsList(IDataList):
    def __init__(self):
        self.__destsList: list = []

    #
    # adds an item to the destinations list
    def add(self, item: MessageDestination):
        if item is None or not isinstance(item, MessageDestination):
            raise Exception("Invalid object reference for adding item to message destinations list.")

        # add to the list
        self.__destsList.append(item)

    #
    # gets an item from the destinations list
    def get(self, idx: int) ->MessageDestination:
        if idx < 0 or idx > len(self.__destsList) - 1:
            raise Exception("Index is out of range for message destination item.")

        return self.__destsList[idx]

    #
    # gets the number of items in the destinations list
    def getCount(self) ->int:
        return len(self.__destsList)

    #
    # yields an item from the message destinations list
    def __iter__(self):
        for md in self.__destsList:
            yield md