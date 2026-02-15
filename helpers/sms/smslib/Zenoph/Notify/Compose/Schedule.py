from datetime import datetime
from Zenoph.Notify.Utils.MessageUtil import MessageUtil

class Schedule(object):
    def __init__(self):
        self.__dateTime: datetime = None
        self.__utcOffset: str = None

    def __validateScheduling(self, dt: datetime):
        if dt is None or isinstance(dt, datetime) == False:
            raise Exception("Invalid datetime object reference for scheduling message.")

    def setScheduleDateTime(self, dt: datetime, val1: str = None, val2: str = None):
        if dt is None:
            self.__dateTime = None
            self.__utcOffset = None
        else:
            self.__validateScheduling(dt)
            self.__dateTime = dt

            # if both val1 and val2 are unset, then only dateTime is to be set
            if val1 is None and val2 is None:
                self.__utcOffset = None
                return

            # at this point val1 must be provided
            if val1 is None:
                raise Exception("Missing time zone region or UTC offset.")

            if val1 is not None and val2 is not None:
                self.__utcOffset = self.__getRegionOffset(val1, val2)
            elif val1 is not None and val2 is None:
                # ensure the UTC offset is in the correct format
                if not MessageUtil.isValidTimeZoneOffset(val1):
                    raise Exception("The specified time zone offset '%s' is invalid or not in the correct format." % val1)

                # set scheduling UTC offset
                self.__utcOffset = val1

    def __getRegionOffset(self, region: str, city: str) ->str:
        # go through the time zones to see if there is region and city combination
        timeZones = MessageUtil.getTimeZones()
        utcOffset = None
        found = False

        if timeZones is None:
            raise Exception("Time zones data has not been loaded.")

        # iterate through the time zones dictionary
        for regionKey in timeZones:
            if regionKey.lower() != region.lower():
                continue

            # get the cities values. It is a list of a list (the inner list contains the city name and utc offset)
            citiesList = timeZones[regionKey]

            for cityInfo in citiesList:
                if cityInfo[0].lower() == city.lower():
                    utcOffset = cityInfo[1]
                    found = True
                    break 

            # if found, break outer loop
            if found:
                break

        return utcOffset

    #
    # get schedule date time
    def getDateTime(self) ->datetime:
        return self.__dateTime

    #
    # gets scheduling UTC offset
    def getUTCOffset(self) ->str:
        return self.__utcOffset
