from xml.dom import pulldom

from Zenoph.Notify.Store.UserData import UserData
from Zenoph.Notify.Enums.AuthModel import AuthModel

class AuthProfile(object):
    def __init__(self):
        self.__authLogin = None
        self.__authPsswd = None
        self.__authApiKey = None
        self.__authModel = None
        self.__authed = False
        self.__userData = None

    #
    # indicates whether account has been authenticated or not
    def authenticated(self) ->bool:
        return self.__authed

    #
    # gets user data
    def getUserData(self) ->UserData:
        return self.__userData

    #
    # extracts user data
    def extractUserData(self, doc):
        self.__userData = UserData.create(doc)
        self.__authed = True

    #
    # sets account authentication model
    def setAuthModel(self, model: AuthModel):
        self.__authModel = model

    #
    # gets authentication model
    def getAuthModel(self) ->AuthModel:
        return self.__authModel

    #
    # sets account authentication login
    def setAuthLogin(self, login: str):
        if login is None or len(login) == 0:
            raise Exception("Invalid value for setting account authentication login.")

        # set login
        self.__authLogin = login

    #
    # gets account authentication login
    def getAuthLogin(self):
        return self.__authLogin

    #
    # sets the account password for authentication
    def setAuthPassword(self, psswd: str):
        if psswd is None or len(psswd) == 0:
            raise Exception("Invalid value for setting account password for authentication.")

        # set password
        self.__authPsswd = psswd

    #
    # gets the account authentication password
    def getAuthPassword(self):
        return self.__authPsswd

    #
    # sets the API key for authentication
    def setAuthApiKey(self, key: str):
        if key is None or len(key) == 0:
            raise Exception("Invalid value for setting API key for authentication.")

        # set the key
        self.__authApiKey = key

    #
    # gets the authentication API key
    def getAuthApiKey(self):
        return self.__authApiKey
