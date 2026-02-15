import re
from base64 import b64decode
from xml.dom import pulldom
from xml.etree import ElementTree

from Zenoph.Notify.Request.RequestException import RequestException
from Zenoph.Notify.Enums.RequestHandshake import RequestHandshake
from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Utils.RequestUtil import RequestUtil
from Zenoph.Notify.Utils.XMLUtil import XMLUtil


class APIResponse(object):
    __responsePattern = b"<response><handshake>.+<\/handshake>(<data>(.*)<\/data>)?<\/response>"

    def __init__(self):
        self._httpStatusCode: int = 0
        self._dataFragment: str = ""
        self._handshake: RequestHandshake = RequestHandshake.HSHK_ERR_UNKNOWN

    @staticmethod
    def create(data: list):
        if data is None or len(data) != 3:
            raise Exception("Invalid reference to object for creating API response data.")
        
        statusCode: int = data[0]
        contentTypeLabel: str = data[1]
        responseStr: str = data[2]

        # ensure we have a valid content type label
        if not RequestUtil.isValidDataContentTypeLabel(contentTypeLabel):
            raise Exception("Unknown response content type label.")

        contentType = RequestUtil.getDataContentTypeFromLabel(contentTypeLabel)

        # for gzip compressed data, we will have to deflate
        if contentType == ContentType.GZBIN_XML or contentType == ContentType.GZBIN_JSON or contentType == ContentType.GZBIN_WWW_URL_ENCODED:
            compressedData = b64decode(responseStr)

            if compressedData is None or len(compressedData) == 0:
                raise Exception("Invalid response data for submitted request.")

            responseStr = RequestUtil.gzDecompressData(compressedData)

        # initialise API response object
        apiResp = APIResponse()
        apiResp.__initResponse(statusCode, responseStr)

        # return API response object
        return apiResp

    def __initResponse(self, httpCode: int, responseStr: str):
        if not self.__isValidAPIResponse(responseStr):
            raise Exception("Unknown response data was received from the server.")

        self._httpStatusCode = httpCode
        self.__extractData(responseStr)
        self.__assertRequestHandshake()

    def __isValidAPIResponse(self, responseStr: str) ->bool:
        match = re.search(APIResponse.__responsePattern, responseStr, re.DOTALL)
       
        # if it matched, then it will not be None
        return not match is None

    def __extractData(self, responseStr: str):
        doc = XMLUtil.createXMLDocument(responseStr.decode(RequestUtil.TEXT_ENCODING_UTF8))

        for event, node in doc:
            if event == pulldom.START_ELEMENT and node.localName == "handshake":
                doc.expandNode(node)
                innerXml = node.toxml()
                tree = ElementTree.fromstring(innerXml)
                self._handshake = RequestHandshake(int(tree.find("id").text))
            elif event == pulldom.START_ELEMENT and node.localName.lower() == "data":
                doc.expandNode(node)
                self._dataFragment = node.toxml()
                return

    def __assertRequestHandshake(self):
        if self._handshake != RequestHandshake.HSHK_OK:
            msg = "Request handshake failure:"

            if self._handshake == RequestHandshake.HSHK_ERR_RH_CONTENT_TYPE:
                raise RequestException("%s Missing or invalid request content type." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_RH_HTTP_ACCEPT:
                raise RequestException("%s Missing or invalid response content type." % msg, self._handshake)
            # group id 12
            elif self._handshake == RequestHandshake.HSHK_ERR_UA_AUTH:
                raise RequestException("%s Authentication failed." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_UA_MODEL:
                raise RequestException("%s Missing or invalid authentication model." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_UA_PID:
                raise RequestException("%s Missing or invalid authentication PID." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_UA_API_NO_ACCESS:
                raise RequestException("%s API access is disabled in your account." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_UA_API_NO_PPASS:
                raise RequestException("%s Portal authentication factor is disabled over API calls." % msg, self._handshake)
            # GROUP ID 14: Unable to understand request
            elif self._handshake == RequestHandshake.HSHK_ERR_DATA:
                raise RequestException("%s Missing request data." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_BAD_REQUEST:
                raise RequestException("%s Bad request." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_INTERNAL:
                raise RequestException("%s Internal server error." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_ACCESS_DENIED:
                raise RequestException("%s Access denied for request." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_API_RETIRED:
                raise RequestException("%s The API version for the request has been retired." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SERVICE:
                raise RequestException("%s Service request not granted." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_ACCT_INACTIVE:
                raise RequestException("%s Account is inactive." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_ACCT_SUSPENDED:
                raise RequestException("%s Account is suspended." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_IDEMPOTENCY_KEY:
                raise RequestException("%s Invalid request idempotency key." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_API_VERSION:
                raise RequestException("%s Missing or invalid request API version." % msg, self._handshake)
            # GROUP ID 18 (for scheduled messages requests)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_PROCESSED:
                raise RequestException("%s The scheduled message is already processed." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_NOT_SCHEDULED:
                raise RequestException("%s The specified message was not scheduled." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_CATEGORY:
                raise RequestException("%s Missing or invalid scheduled messages category." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_DATETIME:
                raise RequestException("%s Missing or invalid date and time for loading scheduled messages." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_CANCELLED:
                raise RequestException("%s Scheduled message was cancelled." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_REFERENCE_ID:
                raise RequestException("%s Missing or invalid scheduled message reference identifier." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_MESSAGE_ID:
                raise RequestException("%s Missing or invalid scheduled message identifier." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_SM_UTC_OFFSET:
                raise RequestException("%s Invalid scheduled message timezone offset." % msg, self._handshake)
            # GROUP ID: 15
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_BATCH_ID:
                raise RequestException("%s Missing or invalid message batch identifier." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_DESTINATIONS:
                raise RequestException("%s Invalid message destinations parameter." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_PARAMETER:
                raise RequestException("%s Missing or invalid request parameter." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_QUERY_TIME:
                raise RequestException("%s Message request time." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_VOICE_FILE:
                raise RequestException("%s Missing or invalid voice message file." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_VOICE_SIZE:
                raise RequestException("%s Voice message file size limit exceeded." % msg, self._handshake)
            elif self._handshake == RequestHandshake.HSHK_ERR_MR_STATUS_FILTER:
                raise RequestException("%s Missing or invalid message status filter." % msg, self._handshake)
            # unknown
            else:
                raise RequestException("%s Unknown request handshake error." % msg, self._handshake)

    def getDataFragment(self) ->str:
        return self._dataFragment

    def getHttpStatusCode(self) ->int:
        return self._httpStatusCode

    def getRequestHandshake(self) ->RequestHandshake:
        return self._handshake
