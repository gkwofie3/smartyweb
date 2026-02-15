import abc
from datetime import datetime

from Zenoph.Notify.Build.Writer.IDataWriter import IDataWriter
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Enums.AuthModel import AuthModel
from Zenoph.Notify.Compose.Composer import Composer
from Zenoph.Notify.Utils.MessageUtil import MessageUtil

class DataWriter(IDataWriter):
    __AUTH_FACTOR_SEPARATOR__ = "__::"

    def __init__(self):
        self._authModel = None
        self._authApiKey = None
        self._authLogin = None
        self._authPsswd = None
        self._authLoadPS = False

    @abc.abstractmethod
    def _writeDestinations(self, mc: Composer, store: dict):
        pass

    @abc.abstractmethod
    def _writeCommonMessageProperties(self, mc: Composer, store: dict):
        pass

    @abc.abstractmethod
    def _writeScheduleInfo(self, dt: datetime, offset: str, store: dict):
        pass

    @abc.abstractmethod
    def _writeCallbackInfo(self, url: str, type: ContentType, store: dict):
        pass

    @staticmethod
    def create(type: ContentType):
        pass

    #
    # sets the authentication model for the request
    def setAuthModel(self, model: AuthModel):
        if model is None or isinstance(model, AuthModel) == False:
            raise Exception("Invalid object reference for authentication model.")

        self._authModel = model

    #
    # sets the API key for request authentication
    def setAuthApiKey(self, key: str):
        if key is None or not isinstance(key, str) or len(key) == 0:
            raise Exception("Invalid API key for writing request authentication data.")

        # set the API key
        self._authApiKey = key

    #
    # sets account login for authentication
    def setAuthLogin(self, login: str):
        if login is None or len(login) == 0:
            raise Exception("Invalid login for writing request authentication data.")

        # set the login
        self._authLogin = login

    #
    # sets account password for request authentication
    def setAuthPassword(self, psswd: str):
        if psswd is None or len(psswd) == 0:
            raise Exception("Invalid password for writing request authentication data.")

        # set the password
        self._authPassword = psswd

    #
    def setAuthPSLoad(self, load: bool):
        self._authLoadPS = True if load == True else False

    # validates scheduling info data
    def _validateScheduleInfo(self, dt: datetime, offset: str):
        if dt is None or not isinstance(dt, datetime):
            raise Exception("Invalid datetime object for writing message scheduling data.")

        if offset is not None:
            if not isinstance(offset, str) or len(offset) == 0 or not MessageUtil.isValidTimeZoneOffset(offset):
                raise Exception("Invalid time zone UTC offset for writing message scheduling data.")

    #
    # validates scheduled message load request data
    def _validateScheduledMessagesLoadData(self, data: dict):
        if data is None or not isinstance(data, dict) or len(data) == 0:
            raise Exception("Invalid object for writing scheduled messages request data.")

        if not "category" in data:
            raise Exception("Message category parameter has not been set for writing scheduled message request data.")

        if not "dateFrom" in data:
            raise Exception("Date 'From' parameter has not been set for writing scheduled message request data.")

        if not "dateTo" in data:
            raise Exception("Date 'To' parameter has not been set for writing scheduled message request data.")

        if not "offset" in data:
            raise Exception("Time zone UTC offset parameter has not been set for writing scheduled message request data.")

        if not "batch" in data:
            raise Exception("Message batch identifier has not been set for writing scheduled message request data.")

    # validates delivery notification info data
    def _validateDeliveryNotificationInfo(self, url: str, contentType: ContentType):
        if url is None or not isinstance(url, str) or len(url) == 0:
            raise Exception("Invalid URL for message delivery notifications.")

        # only xml or JSON is supported for this
        if contentType is None or (contentType != ContentType.DCT_XML and contentType != ContentType.DCT_JSON):
            raise Exception("Unsupported response content type for message delivery notifications.")
