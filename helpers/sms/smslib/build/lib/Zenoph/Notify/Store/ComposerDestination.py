from Zenoph.Notify.Enums.DestinationMode import DestinationMode

class ComposerDestination(object):
    def __init__(self):
       self.__destMode: DestinationMode = DestinationMode.DM_NONE
       self.__phoneNumber: str
       self.__messageId: str
       self.__data: object
       self.__scheduled: bool = False

    # creates composer destination object
    @staticmethod
    def create(data: object):
        if data is None or type(data) is not dict:
            raise Exception("Invalid object reference for initialising composer destination.")

        # perform validation
        ComposerDestination.__validateInitData(data)

        # initialise and set values
        cd = ComposerDestination()
        cd.__destMode = data["destMode"]
        cd.__phoneNumber = data["phoneNumber"]
        cd.__messageId = data["messageId"]
        cd.__scheduled = data["scheduled"]
        cd.__data = data["data"]

        return cd

    @staticmethod
    def __validateInitData(data: dict):
        if not "destMode" in data or not type(data["destMode"]) == DestinationMode:
            raise Exception("Destination mode specifier not set or invalid.")

        if not "phoneNumber" in data or (data["phoneNumber"] is None or data["phoneNumber"] == ""):
            raise Exception("Phone number invalid or not specified for composer destination.")

        if not "messageId" in data:
            raise Exception("Message identifier invalid or not specified for composer destination.")

        if not "data" in data:
            raise Exception("Data not specified for composer destination.")

        if not "scheduled" in data or not type(data["scheduled"]) == bool:
            raise Exception("Destination schedule specifier invalid or has not been set.")

    # resets object
    def reset(self):
        if not self.__scheduled:
            raise Exception("Cannot reset write mode for non-scheduled destination.")

        # perform the reset to none
        self.__destMode = DestinationMode.DM_NONE

    # gets phone number
    def getPhoneNumber(self) ->str:
        return self.__phoneNumber

    # gets messageId
    def getMessageId(self) ->str:
        return self.__messageId

    # gets destination write mode
    def getWriteMode(self) ->DestinationMode:
        return self.__destMode

    # gets data
    def getData(self) ->object:
        return self.__data

    # indicates whether message was scheduled or not (scheduled messages can be loaded)
    def isScheduled(self) ->bool:
        return self.__scheduled
