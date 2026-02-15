import enum

class ContentType(enum.Enum):
    XML = 0
    JSON = 1
    WWW_URL_ENCODED = 2
    MULTIPART_FORM_DATA = 3
    GZBIN_XML = 4
    GZBIN_JSON = 5
    GZBIN_WWW_URL_ENCODED = 6
