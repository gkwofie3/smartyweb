import gzip
from datetime import datetime

from Zenoph.Notify.Enums.ContentType import ContentType
from Zenoph.Notify.Utils.MessageUtil import MessageUtil

class RequestUtil(object):
    TEXT_ENCODING_UTF8 = "utf-8"
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    DCTL_APPLICATION_XML = "application/xml"
    DCTL_APPLICATION_JSON = "application/json"
    DCTL_MULTIPART_FORM_DATA = "multipart/form-data"
    DCTL_APPLICATION_URL_ENCODED = "application/x-www-form-urlencoded"
    DCTL_APPLICATION_GZBIN_XML = "application/vnd.zenoph.zbm.gzbin+xml"
    DCTL_APPLICATION_GZBIN_JSON = "application/vnd.zenoph.zbm.gzbin+json"
    DCTL_APPLICATION_GZBIN_URL_ENCODED = "application/vnd.zenoph.zbm.gzbin+urlencoded"

    @staticmethod
    def __getContentTypeLabelMaps() ->dict:
        maps: dict = {
                ContentType.XML: RequestUtil.DCTL_APPLICATION_XML,
                ContentType.JSON: RequestUtil.DCTL_APPLICATION_JSON,
                ContentType.WWW_URL_ENCODED: RequestUtil.DCTL_APPLICATION_URL_ENCODED,
                ContentType.GZBIN_XML: RequestUtil.DCTL_APPLICATION_GZBIN_XML,
                ContentType.GZBIN_JSON: RequestUtil.DCTL_APPLICATION_GZBIN_JSON,
                ContentType.GZBIN_WWW_URL_ENCODED: RequestUtil.DCTL_APPLICATION_GZBIN_URL_ENCODED,
                ContentType.MULTIPART_FORM_DATA: RequestUtil.DCTL_MULTIPART_FORM_DATA
            }

        return maps

    @staticmethod
    def isValidDataContentTypeLabel(label: str) ->bool:
        try:
            type = RequestUtil.getDataContentTypeFromLabel(label)

            # found so return true
            return True
        except Exception:
            return False

    @staticmethod
    def getDataContentTypeLabel(type: ContentType) ->str:
        label = RequestUtil.__getContentTypeLabelMaps().get(type, None)

        if label is None:
            raise Exception("Unknown data content type specifier for label.")

        # return label
        return label

    @staticmethod
    def getDataContentTypeFromLabel(label: str) ->ContentType:
        if label is None or len(label.strip()) == 0:
            raise Exception("Invalid content type label for validation.")

        labelLower = label.lower()
        typeMaps = RequestUtil.__getContentTypeLabelMaps()

        for key in typeMaps:
            if typeMaps[key].lower() == labelLower:
                return key

        raise Exception("Content type label '%s' was not found." % label)

    @staticmethod
    def isRegexMatch(pattern: str, value: str, dotAllMode: bool = False):
        return MessageUtil.isRegexMatch(pattern, value, dotAllMode)

    @staticmethod
    def dateTimeToStr(dt: datetime) ->str:
        if dt is None or not isinstance(dt, datetime):
            raise Exception("Invalid datetime object for convertion.")

        # convert to string format
        return dt.strftime(RequestUtil.DATE_TIME_FORMAT)

    @staticmethod
    def dateStrToObj(dateStr: str) ->datetime:
        if not RequestUtil.isRegexMatch(RequestUtil.DATE_TIME_FORMAT, dateStr):
            raise Exception("Invalid date time text for conversion.")

        return datetime.strptime(dateStr, RequestUtil.DATE_TIME_FORMAT)

    @staticmethod
    def gzCompressData(data: str) ->str:
        return gzip.compress(data)

    @staticmethod
    def gzDecompressData(data: str) ->str:
        return gzip.decompress(bytes(data))