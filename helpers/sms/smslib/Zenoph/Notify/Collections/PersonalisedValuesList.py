from Zenoph.Notify.Collections.IDataList import IDataList
from Zenoph.Notify.Store.PersonalisedValues import PersonalisedValues

class PersonalisedValuesList(IDataList):
    def __init__(self):
        self.__valuesList: list = []

    def export(self) ->list:
        tempList = []

        for pv in self.__valuesList:
            tempList.append(pv.export())

        # return the list
        return tempList

    def add(self, item: PersonalisedValues):
        if item is None or isinstance(item, PersonalisedValues) == False:
            raise Exception("Invalid object reference for adding personalised values list item.")

        # add to values list
        self.__valuesList.append(item)

    def get(self, idx: int) ->PersonalisedValues:
        if idx < 0 or idx > len(self.__valuesList) - 1:
            raise Exception("Index out of range for getting personalised values.")

        return self.__valuesList[idx]

    def getCount(self) ->int:
        return len(self.__valuesList)

    def __iter__(self):
        for pv in self.__valuesList:
            yield pv


