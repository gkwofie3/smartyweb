from abc import ABC
#from Zenoph.Notify.Compose import IComposer
#from Zenoph.Notify.Store import AuthProfile, UserData
#from Zenoph.Notify.Enums import DataContentType

from Zenoph.Notify.Compose.IComposer import IComposer
from Zenoph.Notify.Store.UserData import UserData
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Store.ComposerDestination import ComposerDestination
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Enums.NumberAddInfo import NumberAddInfo
from Zenoph.Notify.Utils.PhoneUtil import PhoneUtil
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Collections.ComposerDestinationsList import ComposerDestinationsList

class Composer (IComposer):
    __DEST_COUNTRYCODE_LABEL__ = "countryCode"
    __DEST_INFO_LABEL__ = "destInfo"
    __PHONE_NUMBER_LABEL__ = "number"

    def __init__(self, ap: AuthProfile = None):
        self._userData: UserData = None
        self._destinations: list = []
        self._destIdsMap: dict = {}
        self._destNumbersMap: dict = {}
        self._scheduleDateTime = None
        self._scheduleUTCOffset = None
        self._category = None

        if ap is not None:
            if isinstance(ap, AuthProfile) == False:
                raise Exception("Invalid parameter for initialising message object.")

            # authProfile must be authenticated
            if ap.authenticated() == False:
                raise Exception("User profile object has not been authenticated.")

            # set user data from auth profile
            self._userData = ap.getUserData()

    # sets user data
    def setUserData(self, ud: UserData):
        if ud is None or isinstance(ud, UserData) == False:
            raise Exception("Invalid user data reference.")

        # set the user data
        self._userData = ud

    def getCategory(self):
        return self._category

    #
    # gets country name for specified phone number
    def getDestinationCountry(self, phoneNumber: str) ->str:
        if self._userData is None:
            return None

        # destination phone number must exist
        if not self.destinationExists(phoneNumber):
            return None

        numberInfo = self._formatPhoneNumber(phoneNumber)
        fmtdNumber = numberInfo[Composer.__PHONE_NUMBER_LABEL__]
        countryCode = self._getDestinationCountryCode(fmtdNumber)

        if countryCode is None or countryCode == "":
            return None

        # get route filters and check country code
        filters = self._userData.getRouteFilters()

        if not countryCode in filters:
            return None

        # get and return the country name
        return filters[countryCode]["countryName"]

    #
    # gets country name for client default destination
    def getDefaultDestinationCountry(self):
        if self._userData is None:
            raise Exception("Default destination country has not been loaded.")

        # default route information
        defRouteInfo = self._userData.getDefaultRouteInfo()

        countryName = defRouteInfo["countryName"]
        countryCode = defRouteInfo["countryCode"]
        numberPrefix = defRouteInfo["dialCode"]

        return [countryName, countryCode, numberPrefix]

    #
    # gets country number prefix for specofied phone number
    def _getDestinationCountryCode(self, phoneNumber: str) ->str:
        countryCode = None

        # if the phone number has already been added, then quickly get the country code
        if self._formattedDestinationExists(phoneNumber):
            countryCode = self._destNumbersMap[phoneNumber][Composer.__DEST_COUNTRYCODE_LABEL__]
        else:
            numberInfo = self._formatPhoneNumber(phoneNumber)

            if numberInfo is None:
                return None

            # get the country code
            countryCode = numberInfo[Composer.__DEST_COUNTRYCODE_LABEL__]

        # return the country code
        return countryCode

    #
    # gets destination write mode
    def getDestinationWriteMode(self, phoneNumber: str):
        if phoneNumber is None or len(phoneNumber.stip()) == 0:
            raise Exception("Invalid phone number for destination write mode.")

        # phone number should exist in destinations
        if not self.destinationExists(phoneNumber):
            raise Exception(f"Phone number '{phoneNumber}' does not exist in destinations list.")

        # format phon number
        numInfo = self._formatPhoneNumber(phoneNumber)
        fmtdNumber = numInfo[Composer.__PHONE_NUMBER_LABEL__]

        # get destinations data
        destsInfoList = self._getMappedDestinations(fmtdNumber)

        # we don't expect multiple records
        if len(destsInfoList) > 1:
            raise Exception("There are multiple destinations data information.")

        return destsInfoList[0].getWriteMode()

    #
    # gets destination write mode using messageId
    def getDestinationWriteModeById(self, messageId: str):
        if messageId is None or len(messageId.strip()) == 0:
            raise Exception("Invalid message identifier for getting destination write mode.")

        # it should exist in the message Ids list
        if not messageId in self._destIdsMap:
            raise Exception(f"Message identifier '{messageId}' does not exist.")

        return self._destIdsMap[messageId].getWriteMode()

    #
    # gets composer destinations mapped to by the specified phone number
    def _getMappedDestinations(self, phoneNumber: str) ->list:
        if phoneNumber is None or len(phoneNumber.strip()) == 0:
            raise Exception("Invalid phone number for mapped composer destination.")

        if not phoneNumber in self._destNumbersMap:
            raise Exception(f"'{phoneNumber}' does not exist in destinations list.")

        return self._destNumbersMap[phoneNumber][Composer.__DEST_INFO_LABEL__]

    #
    # gets composer destination mapped to by specified messageId
    def _getMappedDestinationById(self, destId: str) ->ComposerDestination:
        if destId is None or len(destId.strip()) == 0:
            raise Exception("Invalid message identifier for composer destination.")

        # it must exist
        if not self.destinationIdExists(destId):
            raise Exception(f"Message identifier '{destId}' does not exist.")

        # return compose destination mapped to by this messageId
        return self._destIdsMap[destId]

    #
    # gets composer destination for specified messageId
    def _getComposerDestinationById(self, destId: str) ->ComposerDestination:
        return self._getMappedDestinationById(destId)

    #
    # get composer destinations for specified phone number
    def _getComposerDestinations(self, phoneNumber: str) ->list:
        return self._getMappedDestinations(phoneNumber)

    #
    # checks if formatted destination exists
    def _formattedDestinationExists(self, phoneNumber: str) ->bool:
        if self._destNumbersMap is None or len(self._destNumbersMap) == 0:
            return False

        return phoneNumber in self._destNumbersMap

    #
    # checks if destination exists. The phone number does not necessarily have to be formatted into international number format
    def destinationExists(self, phoneNumber: str):
        if phoneNumber is None or len(phoneNumber.strip()) == 0:
            raise Exception("Invalid reference to phone number for verification.")

        # convert number into international format before checking
        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            return False

        return self._formattedDestinationExists(numberInfo[Composer.__PHONE_NUMBER_LABEL__])

    #
    # formats phone number into international number format
    def _formatPhoneNumber(self, phoneNumber: str, throwEx = False):
        if self._userData is None:
            return UserData.createDestinationCountryMap(phoneNumber, None)
        else:
            return self._userData.formatPhoneNumber(phoneNumber, throwEx)
    
    #
    # gets formatted phone number
    def _getFormattedPhoneNumber(self, phoneNumber: str) ->str:
        if phoneNumber is None or len(phoneNumber.strip()) == 0:
            raise Exception("Invalid reference to phone number for verification.")

        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            raise Exception("Invalid or unsupported phone number.")

        return numberInfo[Composer.__PHONE_NUMBER_LABEL__]

    #
    # clears message destinations list
    def clearDestinations(self):
        self._destIdsMap.clear()
        self._destinations.clear()
        self._destNumbersMap.clear()

    #
    # adds destinations from a text stream
    def addDestinationsFromTextStream(self, txtStr) ->int:
        if txtStr is None or len(txtStr.strip()) == 0:
            raise Exception("Invalid text stream for adding message destinations.")

        addedCount = 0
        validList = PhoneUtil.extractPhoneNumbers(txtStr)

        if validList is not None:
            addedCount = self.addDestinationsFromCollection(validList, False)

        # return count of phone numbers added
        return addedCount

    #
    # adds destinations from collection
    def addDestinationsFromCollection(self, phoneColl: list, throwEx: bool = False) ->int:
        if phoneColl is None:
            if not throwEx:
                return 0

            raise Exception("Invalid collection for adding destinations.")

        count = 0
        for phoneNumer in phoneColl:
            if self.addDestination(phoneNumer, throwEx) == NumberAddInfo.NAI_OK:
                count += 1

        # return count
        return count

    #
    # adds destination
    def addDestination(self, phoneNumber: str, throwEx: bool = False, messageId: str = None):
        if phoneNumber is None or len(phoneNumber.strip()) == 0:
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_INVALID

            # throw exception
            raise Exception("Invalid value for adding message destination.")
        
        if not PhoneUtil.isValidPhoneNumber(phoneNumber):
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_INVALID

            # throw exception
            raise Exception(f"'{phoneNumber}' is not a valid phone number.")

        if messageId is not None and len(messageId.strip()) != 0:
            numAddInfo = self._validateCustomMessageId(messageId, throwEx)

            if numAddInfo != NumberAddInfo.NAI_OK:
                return numAddInfo

        # format phone number
        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_ROUTE

            # throw exception
            raise Exception(f"'{phoneNumber}' is not a valid destination on permitted routes.")

        fmtdNumber = numberInfo[Composer.__PHONE_NUMBER_LABEL__]
        
        # the formatted phone number must not already exist
        if self._formattedDestinationExists(fmtdNumber):
            if not throwEx:
                return NumberAddInfo.NAI_REJTD_EXISTS

            # throw exception
            raise Exception(f"Phone number '{phoneNumber}' already exists.")

        # add
        return self._addDestinationInfo(fmtdNumber, numberInfo[Composer.__DEST_COUNTRYCODE_LABEL__], messageId, None)

    #
    # adds destination info
    def _addDestinationInfo(self, phoneNumber: str, countryCode: str, messageId: str, destData) ->NumberAddInfo:
        # Here, we will be adding destination
        destMode = DestinationMode.DM_ADD

        # create the composer destination
        compDest = self._createComposerDestination(phoneNumber, messageId, destMode, destData)
        self._addComposerDestination(compDest, countryCode)

        # phone number added successfully
        return NumberAddInfo.NAI_OK

    #
    # adds composer destinations list
    def _addComposerDestinationsList(self, compDestList: list, countryCode: str):
        if compDestList is None:
            raise Exception("Invalid reference for adding composer destinations collection.")

        for cd in compDestList:
            self._addComposerDestination(cd, countryCode)

    #
    # adds composer destination
    def _addComposerDestination(self, cd: ComposerDestination, countryCode: str = None):
        messageId = cd.getMessageId()

        if messageId is not None and len(messageId.strip()) != 0:
            # messageId must not already exist
            if messageId in self._destIdsMap:
                raise Exception(f"Message identifier '{messageId}' already exists.")

            # add to the message Ids map
            self._destIdsMap[messageId] = cd

        self._destinations.append(cd)

        # destinations key mapping
        phoneNumber = cd.getPhoneNumber()

        if phoneNumber in self._destNumbersMap:
            compDestsList = self._getMappedDestinations(phoneNumber)
            compDestsList.append(cd)
        else:
            compDestsList = [cd]

            destDict = {Composer.__DEST_COUNTRYCODE_LABEL__: countryCode, Composer.__DEST_INFO_LABEL__: compDestsList}
            self._destNumbersMap[phoneNumber] = destDict

    #
    # creates composer destination object
    def _createComposerDestination(self, phoneNumber: str, messageId: str, destMode: DestinationMode, destData: object, isScheduled: bool = False):
        # set key data mappings
        data = {}
        data["phoneNumber"] = phoneNumber
        data["messageId"] = messageId
        data["destMode"] = destMode
        data["scheduled"] = isScheduled
        data["data"] = destData

        # create and return composer destination object
        return ComposerDestination.create(data)

    #
    # checks if messageId exists
    def destinationIdExists(self, messageId: str) ->bool:
        if messageId is None or len(messageId.strip()) == 0:
            raise Exception("Invalid reference for verifying message identifier.")

        return messageId in self._destIdsMap

    #
    # removes composer destinations list
    def _removeComposerDestinationsList(self, phoneNumber: str, compDestList: list):
        if compDestList is not None and len(compDestList) > 0:
            # For scheduled messages with destinations loaded, we will rather want to update the
            # write mode to DELETE so that they will be removed from the server. For this, we will
            # need a temporal list which we will add again for removal of scheduled destinations on the server
            replacementList = []
            countryCode = self._getDestinationCountryCode(phoneNumber)

            # items count
            count = len(compDestList)

            while count > 0:
                count -= 1
                cd: ComposerDestination = compDestList[count]

                # if scheduled, we will update write mode and add it again
                if cd.isScheduled():
                    # there should be replacement for update
                    messageId: str = cd.getMessageId()
                    data: object = cd.getData()
                    mode: DestinationMode = DestinationMode.DM_DELETE

                    # create new composer destination object for replacement
                    replacementList.append(self._createComposerDestination(phoneNumber, messageId, mode, data, True))

                # remove
                self._removeComposerDestination(cd)

            # if there is any to replace (for loaded scheduled destinations), then add as new (write mode has been modified to DELETE)
            if len(replacementList) > 0:
                self._addComposerDestinationsList(replacementList, countryCode)

    #
    # removes composer destination
    def _removeComposerDestination(self, cd: ComposerDestination) ->bool:
        if not cd in self._destinations:
            return False

        # if there is messageId assigned, disassociate it
        messageId = cd.getMessageId()
        phoneNumber = cd.getPhoneNumber()

        if not messageId is None and len(messageId.strip()) > 0 and messageId in self._destIdsMap:
            self._destIdsMap.pop(messageId)

        # get composer destinations list for the phone number
        compDestsList: list = self._getMappedDestinations(phoneNumber)
        compDestsList.remove(cd)

        # if there is no item in the list now, then the key (phone number) should be disassociated
        if len(compDestsList) == 0:
            self._destNumbersMap.pop(phoneNumber)

        # remove it from the destinations list
        self._destinations.remove(cd)

        # completed successfully
        return True

    #
    # removes composer destination for specified phone number
    def removeDestination(self, phoneNumber: str):
        if phoneNumber is None or len(phoneNumber.strip()) == 0:
            raise Exception("Invalid phone number for removing message destination.")

        numberInfo = self._formatPhoneNumber(phoneNumber)

        if numberInfo is None:
            return False

        # phone number in international format
        fmtdNumber = numberInfo[Composer.__PHONE_NUMBER_LABEL__]

        # destination phone number must exist
        if not self._formattedDestinationExists(fmtdNumber):
            raise Exception("Phone number '%s' does not exist." % phoneNumber)

        self._removeComposerDestinationsList(fmtdNumber, self._getMappedDestinations(fmtdNumber))

        # completedsuccessfully
        return True

    #
    # removes composer destination for specified messageId
    def removeDestinationById(self, destId: str):
        if destId is None or len(destId.strip()) == 0:
            raise Exception("Invalid message identifier for removing destination.")

        # messageId must exist
        if not self.destinationIdExists(destId):
            raise Exception("Message identifier '%s' does not exist." % destId)

        # get the composer destination object for removal
        return self._removeComposerDestination(self._getComposerDestinationById(destId))

    #
    # gets phone number for specified messageId
    def _getPhoneNumberFromMessageId(self, messageId: str):
        if messageId is None or len(messageId.strip()) == 0:
            raise Exception("Invalid message identifier for getting destination phone number.")

        # the messageId should exist
        if not messageId in self._destIdsMap:
            raise Exception("Message identifier '%s' does not exist." % messageId)

        # get and return the phone number
        return self._destIdsMap[messageId].getPhoneNumber()

    #
    # validates custom messageId
    def _validateCustomMessageId(self, messageId: str, throwEx: bool) ->NumberAddInfo:
        if messageId is not None and len(messageId.strip()) > 0:
            # the specified messageId should not already exist
            if messageId in self._destIdsMap:
                if not throwEx:
                    return NumberAddInfo.NAI_REJTD_MSGID_EXISTS

                raise Exception(f"Message identifier '{messageId}' already exists.")

            # validate length
            if len(messageId.strip()) < MessageUtil.CUSTOM_MSGID_MIN_LEN or len(messageId.strip()) > MessageUtil.CUSTOM_MSGID_MAX_LEN:
                if not throwEx:
                    return NumberAddInfo.NAI_REJTD_MSGID_LENGTH

                raise Exception("Invalid length of custom message identifier.")

            # should match allowed pattern
            if not MessageUtil.isRegexMatch("[%s]{%s,}" % ("A-Za-z0-9-", MessageUtil.CUSTOM_MSGID_MIN_LEN), messageId):
                if not throwEx:
                    return NumberAddInfo.NAI_REJTD_MSGID_INVALID

                raise Exception("Message identifier '%s' is not in the correct format." % messageId)

        # validated
        return NumberAddInfo.NAI_OK

    #
    # validates update of destination phone number
    def _validateDestinationUpdate(self, prevPhoneNumber: str, newPhoneNumber: str):
        if prevPhoneNumber is None or len(prevPhoneNumber.strip()) == 0:
            raise Exception("Invalid reference to previous phone number for destination update.")

        if newPhoneNumber is None or len(newPhoneNumber.strip()) == 0:
            raise Exception("Invalid reference to new phone number for destination update.")

        # convert to international number format
        prevNumInfo = self._formatPhoneNumber(prevPhoneNumber)
        newNumInfo = self._formatPhoneNumber(newPhoneNumber)

        if prevNumInfo is None:
            raise Exception("Invalid or unsupported previous phone number for destination update.")

        if newNumInfo is None:
            raise Exception("Invalid or unsupported new phone number for destination update.")

        return {"prev": prevNumInfo, "new": newNumInfo}

    #
    # updates composer destination by setting to it a new phone number
    def _updateComposerDestination(self, cd: ComposerDestination, newPhoneNumber: str) ->bool:
        numInfo = self._formatPhoneNumber(newPhoneNumber)
        countryCode = numInfo[Composer.__DEST_COUNTRYCODE_LABEL__]

        destData: object = cd.getData()
        messageId: str = cd.getMessageId()
        scheduled: bool = cd.isScheduled()
        destMode: DestinationMode = cd.getWriteMode()

        # if scheduled, then we will update write mode
        if scheduled:
            destMode = DestinationMode.DM_UPDATE;

        # create composer destination
        newCompDest = self._createComposerDestination(newPhoneNumber, messageId, destMode, destData, scheduled)

        # remove previous one before adding the new
        if self._removeComposerDestination(cd):
            self._addComposerDestination(newCompDest, countryCode)
            return True

        # at this point it wasn't successful
        return False
    #
    # updates destination
    def updateDestination(self, prevPhoneNumber: str, newPhoneNumber: str) ->bool:
        # validation
        numInfoData: dict = self._validateDestinationUpdate(prevPhoneNumber, newPhoneNumber)
        prevFmtdNumber = numInfoData["pre"]["number"]
        newFmtdNumber = numInfoData["new"]["number"]

        # composer destinations list associatedd with the previous phone number
        compDestsList = self._getMappedDestinations(prevFmtdNumber)
        count = len(compDestsList)

        if count == 0:
            return False

        while count > 0:
            count -= 1
            self._updateComposerDestination(compDestsList[count], newFmtdNumber)

            # return success
            return True

    # updates destination for specified messageId
    def updateDestinationById(self, destId: str, newPhoneNumber: str) ->bool:
        if destId is None or len(destId.strip()) == 0:
            raise Exception("Invalid message identifier for updating destination.")

        # the messageId must exist
        if not self.destinationIdExists(destId):
            raise Exception(f"Message identifier '{destId}' does not exist.")

        # new number must be valid
        if newPhoneNumber is None or len(newPhoneNumber.strip()) == 0 or not PhoneUtil.isValidPhoneNumber(newPhoneNumber):
            raise Exception("Invalid phone number for updating message destination.")

        numInfo = self._formatPhoneNumber(newPhoneNumber)

        if numInfo is not None:
            # we need the composer destination object mapped to by this messageId
            cd = self._getComposerDestinationById(destId)

            # update and return status
            return self._updateComposerDestination(cd, numInfo[Composer.__PHONE_NUMBER_LABEL__])
        else:
            return False

    #
    # gets message destinations
    def getDestinations(self):
        return ComposerDestinationsList(self._destinations)

    #
    # gets destinations count
    def getDestinationsCount(self):
        return len(self._destinations)

    #
    # sets default country number prefix
    def setDefaultNumberPrefix(self, prefix):
        if self._userData is None:
            raise Exception("Authentication request has not been performed.")

        self._userData.setDefaultNumberPrefix(prefix)

    #
    # gets default country number prefix
    def getDefaultNumberPrefix(self):
        if self._userData is None:
            return None
        else:
            return self._userData.getDefaultNumberPrefix()

    #
    # gets route countries
    def getRouteCountries(self):
        if self._userData is None:
            return None
        else:
            return self._userData.getRouteCountries()

    #
    # checks if phone number is allowed on client routes
    def _isRoutesPhoneNumber(self, phoneNumber: str) ->bool:
        if self._userData is None:
            raise Exception("Routes data have not been loaded.")

        # get number info and check if None or not
        numberInfo = self._formatPhoneNumber(phoneNumber)

        # check and return
        return False if numberInfo is None else True

    #
    # gets default time zone
    def getDefaultTimeZone(self):
        if self._userData is None:
            return None

        return self._userData.getDefaultTimeZone()
