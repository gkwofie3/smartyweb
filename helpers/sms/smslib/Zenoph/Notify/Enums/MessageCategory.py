import enum

class MessageCategory(enum.Enum):
    SMS = 1
    VOICE = 2
    USSD = 3

    def __int__(self):
        return self.value