from Zenoph.Notify.Collections.IDataList import IDataList
from Zenoph.Notify.Store.ComposerDestination import ComposerDestination

class ComposerDestinationsList(IDataList):
    def __init__(self, data: list):
        if data is None or not type(data) is list:
            raise Exception("Invalid object reference for composer destinations list.")

        if len(data) == 0:
            raise Exception("There are no items in composer destinations list.")

        self.__destsList = data

    #
    # adds an item to the list
    def add(self, value):
        # ensure the data type of value is ComposerDestination
        if value is None or not type(value) is ComposerDestination:
            raise Exception("Invalid object reference for adding composer destination.")

        # add to the list
        self.__destsList.append(value)

    #
    # gets an item from the list at the specified index
    def get(self, idx: int) ->object:
        if idx < 0 or idx > len(self.__destsList) - 1:
            raise Exception("Index was out of range for list item.")

        return self.__destsList[idx]

    #
    # gets the count of items in the list
    def getCount(self) ->int:
        return len(self.__destsList)

    #
    # yields an item from the composer destinations list
    def __iter__(self):
        for item in self.__destsList:
            yield item
