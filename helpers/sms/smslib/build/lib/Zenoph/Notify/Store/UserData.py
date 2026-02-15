import re
from xml.etree import ElementTree

from Zenoph.Notify.Store import UserData
from Zenoph.Notify.Utils.PhoneUtil import PhoneUtil
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Enums.SMSType import SMSType

class UserData(object):
    def __init__(self):
        self.__textMessageType = None
        self.__routeFilters = None
        self.__messageSenders = None
        self.__defaultRoute: dict = None
        self.__defaultPrefix = None
        self.__timeZone = None

    # formats a phone number into international number format
    def formatPhoneNumber(self, phoneNumber, throwEx: bool = False) ->dict:
        if phoneNumber is None or len(phoneNumber) == 0:
            if not throwEx:
                return None

            raise Exception("Invalid phone number for formatting.")

        # remove number prefixes such as '+', '00', or '0'
        fmtdNumber = PhoneUtil.stripPhoneNumberPrefixes(phoneNumber)

        # if phone number is not in international number format, then we will have to
        # convert it into international number format
        if self.__isNationalPhoneNumber(fmtdNumber, self.__defaultRoute):
            # the default number prefix will be needed to convert into international number format.
            # Since this can be changed, don't rely on the default loaded from server.
            # If we do not have a separate copy saved, we will have to save the server one as default.
            if self.__defaultPrefix is None or len(self.__defaultPrefix) == 0:
                self.__setDefaultNumberPrefixCopy(self.__defaultRoute)

            # now convert to international number format
            fmtdNumber = "%s%s" % (self.__defaultPrefix, fmtdNumber)

        # determine matching from the routes filter
        for countryCode in self.__routeFilters:
            minNumLen = int(self.__routeFilters[countryCode]["cnum_minlen"])    # minimum local number length (without preceding zero)
            maxNumLen = int(self.__routeFilters[countryCode]["cnum_maxlen"])    # maximum local number length (without preceding zero)
            networksFilter = self.__routeFilters[countryCode]["networksFilter"]     # can be None
            numberPrefix = self.__routeFilters[countryCode]["dialCode"]
            countryWideFilter = "^%s[0-9]{%d,%d}$" % (numberPrefix, minNumLen, maxNumLen)

            # check if there is a network filter match
            if networksFilter is not None:
                filterPattern = "(?:%s%s)" % (numberPrefix, networksFilter)
                match = re.compile(filterPattern).search(fmtdNumber)

                if match:
                    return self.createDestinationCountryMap(match.group(0), countryCode)
           
            # At this point no match through network filters. check if area codes are supported
            if self.__routeFilters[countryCode]["usesAreaCodes"] == True:
                areaCodesFilter = self.__routeFilters[countryCode]["areaCodesFilter"]
                filterPattern = "(?:%s%s)" % (numberPrefix, areaCodesFilter)
                match = re.compile(filterPattern).search(fmtdNumber)

                if match:
                    return self.createDestinationCountryMap(match.group(1))

            # if there is still no match at this point, relax filter to 
            # see if it will match only by the country code and length
            if MessageUtil.isRegexMatch(countryWideFilter, fmtdNumber):
                return self.createDestinationCountryMap(fmtdNumber, countryCode)

        # at this point there is no match routes match for the specified phone number
        if not throwEx:
            return None

        raise Exception("Phone number '%s' is not permitted on routes." % phoneNumber)

    # checks if phone number is in local number format or not
    def __isNationalPhoneNumber(self, phoneNumber, defRoute):
        numLen = len(phoneNumber)
        minLen = int(defRoute["minNumLen"])
        maxLen = int(defRoute["maxNumLen"])

        # national number format must be equal or within the minimum and maximum lengths
        return numLen >= minLen and numLen <= maxLen

    # sets default number prefix
    def __setDefaultNumberPrefixCopy(self, defRoute):
        # save a copy of the default number prefix retrieved from the account
        self.__defaultPrefix = str(self.__defaultRoute["dialCode"])

    #
    # checks if specified country number prefix exists in client account
    def __hasCountryNumberPrefix(self, prefix: str) ->bool:
        for countryCode in self.__routeFilters:
            if self.__routeFilters[countryCode]["dialCode"] == prefix:
                return True

        # not found
        return False

    def setDefaultDialCode(self, dialCode: str):
        # must be set to some value
        if dialCode is None or len(dialCode) == 0:
            raise Exception("Invalid value for setting default country number prefix.")

        # clean the input by takinw away any plus or double leading zeroes
        cleaned = re.sub("(\+)|(00)|(0)", "", dialCode)

        if cleaned is None or len(cleaned) == 0:
            raise Exception("Invalid value '%s' for setting default country number prefix." % dialCode)

        # ensure we have numeric characters remaining.
        if not isinstance(cleaned, int):
            raise Exception("Invalid value for default number prefix.")

        # client should have this country prefix
        if not self.__hasCountryNumberPrefix(dialCode):
            raise Exception("Country number prefix '%s' is not supported in permitted routes." % dialCode)

        # set it
        self.__defaultPrefix = dialCode

    def setDefaultNumberPrefix(self, prefix: str):
        self.setDefaultDialCode(prefix)

    # gets default country dial code (number prefix)
    def getDefaultDialCode(self) ->str:
        if self.__defaultPrefix is None or len(self.__defaultPrefix) == 0:
            self.__setDefaultNumberPrefixCopy(self.__defaultRoute)

        # return the default number prefix
        return self.__defaultPrefix

    # gets default country dial code (number prefix). This is an alias of getDefaultDialCode()
    def getDefaultNumberPrefix(self) ->str :
        return self.getDefaultDialCode()

    #
    # gets route countries
    def getRouteCountries(self) ->list:
        if self.__routeFilters is None:
            raise Exception("Route countries have not been loaded.")

        countriesList: list = []

        for countryCode in self.__routeFilters:
            countryName = self.__routeFilters[countryCode]["countryName"]
            numberPrefix = self.__routeFilters[countryCode]["dialCode"]

            # append as a list item
            countriesList.append([countryName, countryCode, numberPrefix])

        # return list
        return countriesList

    @staticmethod
    def createDestinationCountryMap(phoneNumber: str, countryCode: str):
        return {"number": phoneNumber, "countryCode": countryCode}

    @staticmethod
    def create(tree: ElementTree.Element) ->UserData:
        ud = UserData()
        ud.__timeZone = tree.find("settings/user/timeZone").text
        
        # message type
        ud.__textMessageType = SMSType(int(tree.find("settings/user/messageType").text))

        # extract other values
        ud.__defaultRoute = UserData.__extractDefaultRouteInfo(tree)
        ud.__routeFilters = UserData.__extractRouteFilters(tree)
        ud.__messageSenders = UserData.__extractMessageSenders(tree)

        # return the data
        return ud

    @staticmethod
    def __extractDefaultRouteInfo(tree: ElementTree.Element) ->dict:
        routeInfo: dict = {}
        destNode = tree.find("settings/user/defDestination")
        routeInfo["countryName"] = destNode.find("countryName").text
        routeInfo["countryCode"] = destNode.find("countryCode").text
        routeInfo["dialCode"] = int(destNode.find("dialCode").text)
        routeInfo["minNumLen"] = int(destNode.find("minNumLen").text)
        routeInfo["maxNumLen"] = int(destNode.find("maxNumLen").text)

        # return route info
        return routeInfo

    @staticmethod
    def __extractRouteFilters(tree: ElementTree.Element) ->dict:
        filters: dict = {}
        filterNodes = tree.findall("settings/user/routeFilters/filter")
        
        for node in filterNodes:
            item: dict = {}
            countryCode = node.find("countryCode").text
            # networks filter pattern can be null for countries without a network identifier added
            n = node.find("networksFilter")
            item["networksFilter"] = None if n is None or n.text.lower() == "null" else n.text

            # area codes filter pattern (can also be None)
            n = node.find("areaCodesFilter")
            item["areaCodesFilter"] = None if n is None or n.text.lower() == "null" else n.text

            # other values
            item["countryName"] = node.find("countryName").text
            item["usesAreaCodes"] = node.find("usesAreaCodes").text.lower() == "true"
            item["dialCode"] = node.find("dialCode").text
            item["cnum_minlen"] = int(node.find("cnum_minlen").text)
            item["cnum_maxlen"] = int(node.find("cnum_maxlen").text)
            item["registerSender"] = node.find("registerSender").text.lower() == "true"
            item["numericSenderAllowed"] = node.find("numericSenderAllowed").text.lower() == "true"

            filters[countryCode] = item

        # return the filters
        return filters


    @staticmethod
    def __extractMessageSenders(tree: ElementTree.Element):
        baseNode = tree.find("settings/user/messageSenders")

        # it is possible for message senders node to be absent if the user does not
        # have any saved message senders. In this case, baseNode will be null
        if baseNode is None:
            return None

        senders = {}
        smsLabel = MessageUtil.getMessageCategoryLabel(MessageCategory.SMS)
        voiceLabel = MessageUtil.getMessageCategoryLabel(MessageCategory.VOICE)

        # check for registered SMS sender ids
        node = baseNode.find(smsLabel)
        if node is not None:
            senders[smsLabel] = UserData.__pullSenders(baseNode, smsLabel)

        # check for registered voice sender ids
        node = baseNode.find(voiceLabel)
        if node is not None:
            senders[voiceLabel] = UserData.__pullSenders(baseNode, voiceLabel)

        # set allowed countries
        senders["countries"] = UserData.__pullSenderCountries(baseNode)

        # return message sender ids
        return senders

    @staticmethod
    def __pullSenderCountries(baseNode):
        # we will be extracting the countries
        countryNodes = baseNode.findall("countries/country")

        # can be null if no countries permitted
        if countryNodes is None:
            return None

        countries = {}

        # iterate to get all the countries
        for node in countryNodes:
            countryName = node.find("name").text
            countryCode = node.find("code").text

            # add to dictionary
            countries[countryCode] = countryName

        # return countries
        return countries

    @staticmethod
    def __pullSenders(baseNode, categoryLabel: str):
        sendersList = {}
        nodesList = baseNode.findall("%s/sender" % categoryLabel)

        if nodesList != None:
            for node in nodesList:
                senderId = node.find("name").text
                caseSensitive = node.find("caseSensitive").text.lower() == "true"

                # country codes supported for the senderId
                codeNodesList = node.findall("countryCodes/code")

                if codeNodesList is None:
                    continue

                countryCodesList = []

                for codeNode in codeNodesList:
                    countryCodesList.append(codeNode.text)

                # sender id info
                sender = {"sensitive": caseSensitive, "countryCodes": countryCodesList}

                # add to the senderIds list
                sendersList[senderId] = sender

        # return sender Ids list
        return sendersList

    # gets default text message type identifier
    def getDefaultTextMessageType(self) ->SMSType:
        return self.__textMessageType

    # gets route filters
    def getRouteFilters(self):
        return self.__routeFilters

    # gets message sender names
    def getMessageSenders(self):
        return self.__messageSenders

    # gets default time zone
    def getDefaultTimeZone(self) ->list:
        if self.__timeZone is not None:
            return self.__timeZone.split("/")

        # not set
        return None

    # gets default route information
    def getDefaultRouteInfo(self):
        return self.__defaultRoute