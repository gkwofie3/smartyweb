import enum

class SMSType(enum.Enum):
    GSM_DEFAULT = 0
    UNICODE = 1
    FLASH_GSM_DEFAULT = 2
    FLASH_UNICODE = 3

    def __int__(self):
        return self.value
