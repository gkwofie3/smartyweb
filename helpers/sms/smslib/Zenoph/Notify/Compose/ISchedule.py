import abc

class ISchedule (abc.ABC):
    @abc.abstractmethod
    def getBatchId(self):
        pass

    @abc.abstractmethod
    def schedule(self):
        pass

    @abc.abstractmethod
    def isScheduled(self):
        pass

    @abc.abstractmethod
    def getScheduleInfo(self):
        pass

    @abc.abstractmethod
    def setScheduleDateTime(self, dateTime, val1 = None, val2 = None):
        pass

    @abc.abstractmethod
    def refreshScheduledDestinationsUpdate(self, destsList):
        pass
