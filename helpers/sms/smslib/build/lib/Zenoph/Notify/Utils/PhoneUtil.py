import abc
import re

class PhoneUtil(abc.ABC):
    __PHONE_NUM_PATTERN__ = "\+?[0-9]{8,13}"

    def __init__(self):
        pass

    def name(self):
        pass

    @staticmethod
    def isValidPhoneNumber(phoneNumber: str) ->bool:
        match = re.match(PhoneUtil.__PHONE_NUM_PATTERN__, phoneNumber)

        return not match is None

    @staticmethod
    def stripPhoneNumberPrefixes(phoneNumber: str) ->str:
        # remove any non-digits, especially to get rid of the '+' sign, if any
        phoneNumber = re.sub("[^\d]", "", phoneNumber)

        # check for zeroes indicating local or international numbber formats
        if phoneNumber[0:2] == "00":
            phoneNumber = phoneNumber[2:]
        elif phoneNumber[0:1] == "0":
            phoneNumber = phoneNumber[1:]

        # return stripped
        return phoneNumber

    @staticmethod
    def extractPhoneNumbers(str) ->list:
        pass
