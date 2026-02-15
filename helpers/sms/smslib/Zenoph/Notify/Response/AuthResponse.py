from xml.etree import ElementTree

from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Response.APIResponse import APIResponse
from Zenoph.Notify.Utils.MessageUtil import MessageUtil
from Zenoph.Notify.Utils.XMLUtil import XMLUtil

class AuthResponse(APIResponse):
    def __init__(self):
        self.__authProfile: AuthProfile = None

    @staticmethod
    def create(data: list):
        if data is None or not isinstance(data, list) or len(data) == 0:
            raise Exception("Invalid data for creating authentication response object.")

        # initialise
        ar = AuthResponse()
        ar.__authProfile = data[1]
        ar._httpStatusCode = data[0].getHttpStatusCode()
        ar._handshake = data[0].getRequestHandshake()

        # if authProfile is set, we will extract settings
        if ar.__authProfile is not None:
            dataFragment = data[0].getDataFragment()

            if dataFragment is not None and len(dataFragment) != 0:
                # create the XML document
                tree: ElementTree.Element = ElementTree.fromstring(dataFragment)

                ar.__authProfile.extractUserData(tree)
                MessageUtil.extractGeneralSettings(tree)

        # return auth response object
        return ar

    def getAuthProfile(self) ->AuthProfile:
        return self.__authProfile
