import abc

class IDataList(abc.ABC):
    @abc.abstractmethod
    def getCount(self) ->int:
        pass

    @abc.abstractmethod
    def add(self, item: object):
        pass

    @abc.abstractmethod
    def get(self, idx: int) ->object:
        pass