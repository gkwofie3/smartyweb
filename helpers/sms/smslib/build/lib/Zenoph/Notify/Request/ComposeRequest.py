from abc import ABC

from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Enums.DestinationMode import DestinationMode
from Zenoph.Notify.Enums.NumberAddInfo import NumberAddInfo
from Zenoph.Notify.Enums.MessageCategory import MessageCategory
from Zenoph.Notify.Request.NotifyRequest import NotifyRequest

class ComposeRequest(NotifyRequest):
    GZBIN_DESTS_LEVEL = 50000

    def __init__(self, ap = None):
        self._composer = None

        super().__init__(ap)

    def _assertComposer(self):
        if self._composer is None:
            raise Exception("Invalid reference to message composer object.")

    # validates composer dat
    def _validate(self):
        self._assertComposer()

        if self._composer.getDestinationsCount() == 0:
            raise Exception("There are no destinations for submitting message.")

    # gets message composer object
    def getComposer(self):
        return self._composer

    # sets authentication profile
    def setAuthProfile(self, ap: AuthProfile):
        # validate
        self._validateAuthProfile(ap)

        # composer object must already be initialised
        if self._composer is None:
            raise Exception("Composer object has not been initialised.")

        # set the user data
        self._composer.setUserData(ap.getUserData())

        # parent will set auth profile
        super().setAuthProfile(ap)

    # gets countries permitted on client routes
    def getRouteCountries(self):
        self._assertComposer()
        return self._composer.getRouteCountries()

    # gets default number prefix
    def getDefaultNumberPrefix(self) ->str:
        self._assertComposer()
        return self._composer.getDefaultNumberPrefix()

    # sets default number prefix
    def setDefaultNumberPrefix(self, prefix: str):
        self._assertComposer()
        self._composer.setDefaultNumberPrefix(prefix)

    # whether deliver notification should be enabled or not
    def notifyDeliveries(self) ->bool:
        self._assertComposer()
        return self._composer.notifyDeliveries()

    # gets default time zone
    def getDefaultTimeZone(self):
        self._assertComposer()
        return self._composer.getDefaultTimeZone()

    # gets country name for destination phone number
    def getDestinationCountry(self, phoneNumber: str) ->str:
        self._assertComposer()
        return self._composer.getDestinationCountry(phoneNumber)

    # gets default destination country info as array (country name and code)
    def getDefaultDestinationCountry(self):
        self._assertComposer()
        return self._composer.getDefaultDestinationCountry()

    # gets destination write mode
    def getDestinationWriteMode(self, phoneNumber: str) ->DestinationMode:
        self._assertComposer()
        return self._composer.getDestinationWriteMode(phoneNumber)

    # gets destination write mode for specified messageId
    def getDestinationWriteModeById(self, messageId: str) ->DestinationMode:
        self._assertComposer()
        return self._composer.getDestinationWriteModeById(messageId)

    # gets message destinations
    def getDestinations(self):
        self._assertComposer()
        return self._composer.getDestinations()

    # gets destinations count
    def getDestinationsCount(self) ->int:
        self._assertComposer()
        return self._composer.getDestinationsCount()

    # updates destination for specified previous phone
    def updateDestination(self, prevPhoneNumber: str, newPhoneNumber: str) ->bool:
        self._assertComposer()
        return self._composer.updateDestination(prevPhoneNumber, newPhoneNumber)

    # updates destination for specified messageId
    def updateDestinationById(self, messageId: str, newPhoneNumber: str) ->bool:
        self._assertComposer()
        return self._composer.updateDestinationById(messageId, newPhoneNumber)

    # clears message destinations
    def clearDestinations(self):
        self._assertComposer()
        self._composer.clearDestinations()

    # adds destinations from text stream
    def addDestinationFromTextStream(self, txtStr) ->int:
        self._assertComposer()
        return self._composer.addDestinationsFromTextStream(txtStr)

    # adds destinations from collection
    def addDestinationsFromCollection(self, phoneColl, throwEx: bool = False) ->int:
        self._assertComposer()
        return self._composer.addDestinationsFromCollection(phoneColl, throwEx)

    # adds message destination
    def addDestination(self, phoneNumber: str, throwEx: bool = True, messageId: str = None) ->NumberAddInfo:
        self._assertComposer()
        return self._composer.addDestination(phoneNumber, throwEx, messageId)

    # removes message destination phone number
    def removeDestination(self, phoneNumber: str) ->bool:
        self._assertComposer()
        return self._composer.removeDestination(phoneNumber)

    # removes message destination for specified messageId
    def removeDestinationById(self, messageId: str) ->bool:
        self._assertComposer()
        return self.removeDestinationById(messageId)

    # checks to see if destination phone number exists or not
    def destinationExists(self, phoneNumber) ->bool:
        self._assertComposer()
        return self._composer.destinationExists(phoneNumber)

    # gets message category
    def getCategory(self) ->MessageCategory:
        self._assertComposer()
        return self._composer.getCategory()