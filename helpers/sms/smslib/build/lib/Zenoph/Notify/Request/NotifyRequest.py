from base64 import b64encode
from abc import ABC, abstractmethod
from http import client as HttpClient

from Zenoph.Notify.Response.APIResponse import APIResponse
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Enums.HttpStatusCode import HttpStatusCode
from Zenoph.Notify.Enums.AuthModel import AuthModel
from Zenoph.Notify.Store.AuthProfile import AuthProfile
from Zenoph.Notify.Build.Writer.DataWriter import DataWriter
from Zenoph.Notify.Utils.RequestUtil import RequestUtil
from Zenoph.Notify.Build.Writer.XmlDataWriter import XmlDataWriter
from Zenoph.Notify.Build.Writer.MultiPartDataWriter import MultiPartDataWriter
from Zenoph.Notify.Build.Writer.UrlEncodedDataWriter import UrlEncodedDataWriter

class NotifyRequest(ABC):
    __AUTH_FACTOR_SEPARATOR = "__::"
    __API_TARGET_VERSION: int = 5

    DEF_HTTP_PORT: int = 80
    DEF_HTTPS_PORT: int = 443

    def __init__(self, ap: AuthProfile = None):
        self._authProfile: AuthProfile = None

        # set other values
        self._loadAPS = False
        self._contentType = ContentType.XML
        self._acceptType = ContentType.XML
        self._requestResource = None
        self._requestData = None
        self._requestURL: str = None
        self._urlScheme: str = "http"

        self.__host: str = None
        self.__httpPort = NotifyRequest.DEF_HTTP_PORT
        self.__httpsPort = NotifyRequest.DEF_HTTPS_PORT
        self.__secureConn: bool = True
        
        # http connection object
        self.__httpConn = None

        # authentication
        self._authModel = AuthModel.API_KEY
        self._authLogin = None
        self._authPsswd = None
        self._authApiKey = None

        if ap is not None:
            # set the authentication profile
            self._validateAuthProfile(ap)
            self._authProfile: AuthProfile = ap

    def _validateAuthProfile(self, authProfile):
        if not isinstance(authProfile, AuthProfile):
            raise Exception("Invalid authentication profile object.")

        # should be already authenticated
        if authProfile.authenticated() == False:
            raise Exception("User profile object has not been authenticated.")

    def setAuthProfile(self, ap):
        self._validateAuthProfile(ap);

    #@staticmethod
    #def InitShared():

    def setHost(self, host):
        if host == None or len(host) == 0:
            raise Exception("Invalid request host URL.")

        self.__host = host

    def setHttpPort(self, port: int):
        if port is None or not port.isnumeric() or port <= 0:
            raise Exception("Invalid http port number.")

        # set the http port
        self.__httpPort = port

    def setHttpsPort(self, port: int):
        if port is None or not type(port) is int or port <= 0:
            raise Exception("Invalid https port number.")

        # set the port number
        self.__httpsPort = port

    def useSecureConnection(self, secure: bool, port: int = -1):
        if secure is None or not type(secure) == bool:
            raise Exception("Invalid value for setting global connection protocol.")

        # set globally
        self.__secureConn = secure

        # set port if provided
        if port is not None and type(port) == int and port > 0:
            if secure == True:
                NotifyRequest.setHttpsPort(port)
            else:
                NotifyRequest.setHttpPort(port)

    # sets authentication model
    def setAuthModel(self, model):
        if model == AuthModel.API_KEY or model == AuthModel.PORTAL_PASS:
            self._authModel = model
        else:
            raise Exception("Invalid authentication model.")

    # sets authentication login
    def setAuthLogin(self, login):
        if login is None or login == "":
            raise Exception("Missing or invalid account login.")

        # should be called only when auth model is PORTAL_PASS
        if self._authModel != AuthModel.PORTAL_PASS:
            raise Exception("Invalid call for setting account login.")

        # set the account login
        self._authLogin = login

    # sets authentication password
    def setAuthPassword(self, psswd):
        if psswd is None or psswd == "":
            raise Exception("Missing or invalid account password.")

        # should be called only when auth model is PORTAL_PASS
        if self._authModel != AuthModel.PORTAL_PASS:
            raise Exception("Invalid call for setting account password.")

        # set account password
        self._authPsswd = psswd

    # sets API key for authentication
    def setAuthApiKey(self, key):
        if key is None or key == "":
            raise Exception("Missing or invalid API key for authentication.")

        # auth model must be API_KEY
        if self._authModel != AuthModel.API_KEY:
            raise Exception("Invalid call for setting API authentication key.")

        # set API key
        self._authApiKey = key

    # validates authentication info
    def __validateAuth(self):
        if self._authModel == AuthModel.PORTAL_PASS:
            if self._authLogin is None or self._authLogin == "" or self._authPsswd is None or self._authPsswd == "":
                raise Exception("Missing account login and or password.")
        else:
            if self._authApiKey is None or self._authApiKey == "":
                raise Exception("Missing or invalid API key for authentication.")

    # sets request resource URL
    def _setRequestResource(self, res):
        if res is None or res == "":
            raise Exception("Invalid reference to request resource.")

        # set request resource URL
        self._requestResource = res

    # sets request content type
    def setRequestContentType(self, type: ContentType):
        if not self.requestContentTypeSupported(type):
            raise Exception("Unsupported request content type.")

        # set content type
        self._contentType = type

    # sets response content type
    def _setResponseContentType(self, type: ContentType):
        if not self.responseContentTypeSupported(type):
            raise Exception("Unsupported response content type.")
        
        # set content type
        self._acceptType = type

    def requestContentTypeSupported(self, type) ->bool:
        if type == ContentType.XML or type == ContentType.GZBIN_XML or type == ContentType.WWW_URL_ENCODED or type == ContentType.GZBIN_WWW_URL_ENCODED or type == ContentType.MULTIPART_FORM_DATA:
            return True
        else:
            return False

    def responseContentTypeSupported(self, type: ContentType) ->bool:
        return True if type == ContentType.XML or type == ContentType.GZBIN_XML else False

    def _initHttpRequest(self):
        # requestURL = self._getRequestURL()
        self._requestURL = "/v%s/%s" % (NotifyRequest.__API_TARGET_VERSION, self._requestResource)

    def submit(self) ->APIResponse:
        contentTypeLabel = RequestUtil.getDataContentTypeLabel(self._contentType)
        acceptTypeLabel = RequestUtil.getDataContentTypeLabel(self._acceptType)

        # initialise the http connection object
        self.__httpConn = HttpClient.HTTPSConnection(self.__host, self.__httpsPort) if self.__secureConn == True else HttpClient.HTTPConnection(self.__host, self.__httpPort)

        headers = {'Content-Type': contentTypeLabel, "Accept": acceptTypeLabel, "Authorization": self.__getAuthData()}
        postData = self._prepareRequestData()

        try:
            # send request
            self.__httpConn.request("POST", self._requestURL, postData, headers)
        except ConnectionError:
            raise Exception("Could not connect to server.")
        except TimeoutError:
            raise Exception("Request timed out.")
        except Exception as e:
            raise Exception("Request submit error.")

        response = self.__httpConn.getresponse()
        self.__assertRequestHttpStatusCode(response.status)

        data = response.read()  #.decode(RequestUtil.__TEXT_ENCODING_UTF8__)
        self.__httpConn.close()

        # create and return API response object
        return APIResponse.create([response.status, response.getheader("Content-Type"), data])
       
    def _prepareRequestData(self) ->dict:
        postData = {}

        if self._contentType == ContentType.XML or self._contentType == ContentType.JSON or self._contentType == ContentType.MULTIPART_FORM_DATA:
            postData = self._requestData
        elif self._contentType == ContentType.GZBIN_XML or self._contentType == ContentType.GZBIN_JSON:
            postData = RequestUtil.compressData(self._requestData)
        elif self._contentType == ContentType.GZBIN_WWW_URL_ENCODED:
            postData = RequestUtil.gzCompressData(self.__buildHttpQuery(self._requestData["keyValues"]))
        elif self._contentType == ContentType.WWW_URL_ENCODED:
            postData = self.__buildHttpQuery(self._requestData["keyValues"]) 

        return postData

    #
    # builds http query string from list data
    def __buildHttpQuery(self, data: dict) ->str:
        query = ""

        for key in data:
            if len(query) > 0:
                query += "&"

            # append the key value
            query += "%s=%s" % (key, data[key])

        # return the resulting query string
        return query

    def __assertRequestHttpStatusCode(self, statusCode: int):
        if statusCode == int(HttpStatusCode.OK):
            return
        elif statusCode == int(HttpStatusCode.ERROR_BAD_REQUEST):
            raise Exception("Bad request.")
        elif statusCode == int(HttpStatusCode.ERROR_UNAUTHORIZED):
            raise Exception("Unauthorised request.")
        elif statusCode == int(HttpStatusCode.ERROR_FORBIDDEN):
            raise Exception("Forbidden request.")
        elif statusCode == int(HttpStatusCode.ERROR_NOT_FOUND):
            raise Exception("Request resource was not found.")
        elif statusCode == int(HttpStatusCode.ERROR_METHOD_NOT_ALLOWED):
            raise Exception("Request method not allowed.")
        elif statusCode == int(HttpStatusCode.ERROR_NOT_ACCEPTABLE):
            raise Exception("Response content type is not acceptable.")
        elif statusCode == int(HttpStatusCode.ERROR_UNPROCESSABLE):
            raise Exception("Request could not be processed.")
        elif statusCode == int(HttpStatusCode.ERROR_INTERNAL):
            raise Exception("Internal server error.")
        else:
            raise Exception("Unknown request error <%d>." % statusCode)

    def __generateAuthFactor(self) ->str:
        if self._authLogin is None or len(self._authLogin.strip()) == 0:
            raise Exception("Invalid login for generating auth factor.")

        if self._authPsswd is None or len(self._authPsswd.strip()) == 0:
            raise Exception("Invalid password for generating auth factor.")

        factor = "%s%s%s" % (self._authLogin, NotifyRequest.__AUTH_FACTOR_SEPARATOR, self._authPsswd)
        return b64encode(bytes(factor, "utf-8"))

    def __getAuthData(self) ->str:
        if self._authProfile is not None:
            self.__extractAuthInfoFromProfile()

        # validate auth
        self.__validateAuth()
        authStr = ""

        if self._authModel == AuthModel.API_KEY:
            authStr = "key %s" % self._authApiKey
        elif self._authModel == AuthModel.PORTAL_PASS:
            authStr = "factor %s" % self.__generateAuthFactor()
        else:
            raise Exception("Unsupported request authentication model.")

        if self._loadAPS:
            authStr = "%s ls" % authStr

        # return
        return authStr

    #
    # initialises request authentication
    @staticmethod
    def _initRequestAuth(request, param1, param2 = None):
        if request is None or isinstance(request, NotifyRequest) == False:
            raise Exception("Invalid request object reference.")

        # Authentication details will depended on the parameters supplied. If both parameters are provided,
        # then the authentication model is PORTAL_PASS otherwise if the second parameter is not provided,
        # then authentication model is API_KEY
        authModel = AuthModel.API_KEY

        if param2 is not None and isinstance(param2, str) and len(param2) > 0:
            authModel = AuthModel.PORTAL_PASS

        request.setAuthModel(authModel)

        if authModel == AuthModel.API_KEY:
            request.setAuthApiKey(param1)
        else:
            request.setAuthLogin(param1)
            request.setAuthPassword(param2)

    def __extractAuthInfoFromProfile(self):
        self._authModel = self._authProfile.getAuthModel()
        self._authLogin = self._authProfile.getAuthLogin()
        self._authPsswd = self._authProfile.getAuthPassword()
        self._authApiKey = self._authProfile.getAuthApiKey()

    def __validateAuth(self):
        if self._authModel == AuthModel.PORTAL_PASS:
            if self._authLogin is None or len(self._authLogin.strip()) == 0 or self._authPsswd is None or len(self._authPsswd.strip()) == 0:
                raise Exception("Missing or invalid account login and or password.")
            elif self._authApiKey is None or len(self._authApiKey.strip()) == 0:
                raise Exception("Missing or invalid API key for authentication.")

    def _getRequestURL(self) ->str:
        if self._requestResource is None or len(self._requestResource.strip()) == 0:
            raise Exception("Invalid reference to request resource.")

        urlScheme = self._urlScheme if self.__secureConn == True else "%ss" % self._urlScheme
        connPort = self.__httpsPort if self.__secureConn == True else self.__httpPort

        # return the request URL
        return "%s://%s:%d/v%s/%s" % (urlScheme, self.__host, connPort, NotifyRequest.__API_TARGET_VERSION, self._requestResource)

    def _createDataWriter(self) ->DataWriter:
        # return DataWriter.create(self._contentType)
        type = self._contentType

        if type is None or not isinstance(type, ContentType):
            raise Exception("Invalid or unsupported content type for initialising request data writer.")

        if type == ContentType.XML or type == ContentType.GZBIN_XML:
            return XmlDataWriter()
        elif type == ContentType.DCT_WWW_URL_ENCODED or type == ContentType.DCT_GZBIN_WWW_URL_ENCODED:
            return UrlEncodedDataWriter()
        elif type == ContentType.MULTIPART_FORM_DATA:
            return MultiPartDataWriter()
        else:
            raise Exception("Invalid or unsupported content type for initialising request data writer.")
