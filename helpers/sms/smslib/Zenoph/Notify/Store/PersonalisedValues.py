
class PersonalisedValues(object):
    def __init__(self, values: list):
        if values is None or len(values) == 0:
            raise Exception("Invalid items for personalised values.")

        self.__valuesList: list = []

        for val in values:
            if val is None:
                raise Exception("Missing or invalid item for personalised message values.")

            # add to the collection
            self.__valuesList.append(val)

    #
    # gets size of the list
    def getSize(self) ->int:
        return len(self.__valuesList)

    #
    # exports values for the object as new list
    def export(self) ->list:
        values = []

        for val in self.__valuesList:
            values.append(val)

        return values

    def __iter__(self):
        for val in self.__valuesList:
            yield val
